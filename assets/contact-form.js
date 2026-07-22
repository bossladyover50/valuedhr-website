(function(){
  const form=document.querySelector('[data-contact-form]');
  if(!form)return;
  const status=form.querySelector('[data-form-status]');
  const button=form.querySelector('button[type="submit"]');
  form.addEventListener('submit',function(event){
    event.preventDefault();
    const trap=form.querySelector('[name="website"]');
    if(trap&&trap.value)return;
    const name=form.elements.name.value.trim();
    const email=form.elements.email.value.trim();
    const message=form.elements.message.value.trim();
    if(!name){status.textContent='Please enter your full name.';form.elements.name.focus();return;}
    if(!email||!email.includes('@')){status.textContent='Please enter a valid email address.';form.elements.email.focus();return;}
    if(!message){status.textContent='Please tell us briefly how we can help.';form.elements.message.focus();return;}
    button.disabled=true;button.textContent='Sending…';status.textContent='';
    const parts=name.split(/\s+/),lastName=parts.length>1?parts.pop():parts[0],firstName=parts.length>0?parts.join(' '):'';
    const interest=form.elements.interest.value.trim();
    const data=new FormData();
    data.append('xnQsjsdp','2aca8732aae656acfcae029c9788120279dd249885b72e208381c746fb2df0b5');
    data.append('zc_gad','');data.append('xmIwtLD','90334662aaad9766a77f35fd9c1cae3690b70187f9b69263e1bc254ad267fe81e987ad2ff0515dca1b24c559c09d13cb');
    data.append('actionType','TGVhZHM=');data.append('returnURL','null');data.append('ldeskuid','');data.append('LDTuvid','');data.append('aG9uZXlwb3Q','');
    data.append('First Name',firstName);data.append('Last Name',lastName);data.append('Email',email);
    data.append('Phone',form.elements.phone.value.trim());data.append('Company',form.elements.company.value.trim());
    data.append('Lead Source',interest?'Website – '+interest:'Website Contact Form');
    data.append('Description',message+(interest?'\n\nInterested in: '+interest:''));
    fetch('https://crm.zoho.com/crm/WebToLeadForm',{method:'POST',body:data,cache:'no-cache',mode:'no-cors'}).then(function(){
      status.textContent='Thank you. Your message was submitted. We will follow up shortly.';
      button.textContent='✓ Message Sent';button.style.background='#2e7d32';
      if(window.valuedHRTrack)window.valuedHRTrack('lead_submit_success',{interest:interest||'Not specified'});
      form.reset();setTimeout(function(){button.disabled=false;button.textContent='Send My Message';button.style.background='';},3500);
    }).catch(function(){button.disabled=false;button.textContent='Send My Message';status.textContent='We could not send your message. Please call 984-343-1096 or email admin@valuedhr.com.';if(window.valuedHRTrack)window.valuedHRTrack('lead_submit_error');});
  });
})();
