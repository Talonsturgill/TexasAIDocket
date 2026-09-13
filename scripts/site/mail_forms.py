"""Progressive enhancement for the Services enquiry form. No message leaves during typing."""

SCRIPT = r"""<script>
(function(){
  document.querySelectorAll('form[data-desk-form]').forEach(function(form){
    var note=form.querySelector('[data-submit-state]');
    var send=form.querySelector('button[type="submit"]');
    if(!note||!send||!window.fetch||!window.AbortController) return;
    var busy=false, label=send.textContent;
    form.addEventListener('submit',function(ev){
      ev.preventDefault();
      if(busy||!form.reportValidity()) return;
      var payload=Object.fromEntries(new FormData(form).entries());
      var controls=Array.from(form.querySelectorAll('input,textarea,button[type="submit"]'));
      var disabled=controls.map(function(el){return el.disabled;});
      busy=true;
      form.setAttribute('aria-busy','true');
      controls.forEach(function(el){el.disabled=true;});
      send.textContent='Sending';
      note.textContent='Sending your message.';
      note.dataset.state='pending';
      var abort=new AbortController();
      var timer=setTimeout(function(){abort.abort();},15000);
      fetch(form.action.replace('formsubmit.co/','formsubmit.co/ajax/'),{
        method:'POST', signal:abort.signal,
        headers:{'content-type':'application/json','accept':'application/json'},
        body:JSON.stringify(payload)
      }).then(function(r){
        if(!r.ok) throw new Error('unconfirmed');
        return r.json();
      }).then(function(result){
        if(result.success!==true&&result.success!=='true') throw new Error('rejected');
        form.reset();
        note.dataset.state='success';
        note.textContent='Thank you. Your message was accepted. The desk will reply to the email address you gave.';
      }).catch(function(error){
        note.dataset.state='error';
        note.textContent=error.message==='rejected'
          ? 'That did not send. Your message is still here. Try again.'
          : 'A confirmation did not arrive. Your message is still here. Try again.';
      }).finally(function(){
        clearTimeout(timer);
        controls.forEach(function(el,i){el.disabled=disabled[i];});
        form.removeAttribute('aria-busy');
        send.textContent=label;
        busy=false;
      });
    });
  });
})();
</script>"""
