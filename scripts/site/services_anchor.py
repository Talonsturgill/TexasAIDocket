"""Keep the Services enquiry fragment clear of the rendered sticky masthead."""

ENHANCEMENT = """<style>
#start { scroll-margin-top:calc(var(--services-header-height,4rem) + 1rem); }
@media (max-width:56rem) {
  #start { scroll-margin-top:calc(var(--services-header-height,0px) + 1rem); }
}
</style>
<script>
(function(){
  var start=document.getElementById('start'), header=document.querySelector('.masthead');
  if(!start||!header) return;
  function measure(){
    var height=getComputedStyle(header).position==='sticky' ? header.getBoundingClientRect().height : 0;
    start.style.setProperty('--services-header-height',height+'px');
  }
  measure();
  if('ResizeObserver' in window) new ResizeObserver(measure).observe(header);
  addEventListener('resize',measure,{passive:true});
  // A native fragment click can arrive before the resize notification is delivered.
  document.querySelectorAll('a[href="#start"]').forEach(function(link){
    link.addEventListener('click',measure);
  });
})();
</script>"""
