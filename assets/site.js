(function(){
  window.valuedHRTrack=function(event,details){
    var payload=Object.assign({event:event},details||{});
    window.dataLayer=window.dataLayer||[]; window.dataLayer.push(payload);
    if(typeof window.gtag==='function') window.gtag('event',event,details||{});
  };
  document.addEventListener('click',function(e){
    var a=e.target.closest('a'); if(!a)return;
    if(a.getAttribute('href')==='#contact') window.valuedHRTrack('discovery_call_click',{location:a.textContent.trim()});
  });
  function loadMarketing(){
    if(document.getElementById('zsiqscript'))return;
    window.$zoho=window.$zoho||{}; window.$zoho.salesiq=window.$zoho.salesiq||{ready:function(){}};
    var chat=document.createElement('script'); chat.id='zsiqscript'; chat.defer=true; chat.src='https://salesiq.zohopublic.com/widget?wc=siqec7f317f631039c2620c40c836d39c5d369bdd9c7d8978f3f03f7b99a1f78c46'; document.body.appendChild(chat);
    var analytics=document.createElement('script'); analytics.defer=true; analytics.src='https://cdn.pagesense.io/js/valuedhr/256d9da17dfa4f46bd9cbb37c6ef86e2.js'; document.body.appendChild(analytics);
  }
  var consent=localStorage.getItem('valuedhr-consent');
  if(consent==='accepted') loadMarketing();
  if(!consent){
    var banner=document.createElement('div'); banner.className='cookie-banner'; banner.setAttribute('role','dialog'); banner.setAttribute('aria-label','Cookie preferences');
    banner.innerHTML='<p>We use optional analytics and chat tools to improve the site. <a href="/privacy.html">Privacy policy</a></p><div><button data-consent="declined">Essential only</button><button data-consent="accepted">Accept</button></div>';
    var css=document.createElement('style'); css.textContent='.cookie-banner{position:fixed;z-index:9999;left:1rem;right:1rem;bottom:1rem;max-width:760px;margin:auto;padding:1rem 1.25rem;background:#fff;color:#16181d;border:1px solid #d8dce3;border-radius:.75rem;box-shadow:0 12px 36px #0003;display:flex;align-items:center;justify-content:space-between;gap:1rem;font:14px/1.45 system-ui}.cookie-banner p{margin:0}.cookie-banner a{color:#2563eb;text-decoration:underline}.cookie-banner div{display:flex;gap:.5rem}.cookie-banner button{border:1px solid #2563eb;border-radius:.4rem;padding:.55rem .8rem;background:#fff;color:#0a1f3c;font-weight:700;white-space:nowrap}.cookie-banner button[data-consent="accepted"]{background:#2563eb;color:#fff}@media(max-width:600px){.cookie-banner{display:block}.cookie-banner div{margin-top:.75rem}}'; document.head.appendChild(css); document.body.appendChild(banner);
    banner.addEventListener('click',function(e){var choice=e.target.dataset.consent;if(!choice)return;localStorage.setItem('valuedhr-consent',choice);banner.remove();if(choice==='accepted')loadMarketing();});
  }
})();
