(function(){
  var form=document.querySelector('[data-fire-drill-form]');
  if(!form)return;
  var status=form.querySelector('[data-form-status]');
  var button=form.querySelector('button[type="submit"]');
  var confirmation=document.querySelector('[data-confirmation]');

  function updateCount(fieldName,countId){
    var field=form.elements[fieldName];
    var count=document.getElementById(countId);
    function render(){count.textContent=field.value.length.toLocaleString()+' / '+field.maxLength.toLocaleString();}
    field.addEventListener('input',render);render();
  }
  updateCount('summary','summary-count');
  updateCount('outcome','outcome-count');

  function showError(field,message){
    status.textContent=message;status.classList.add('error');
    field.setAttribute('aria-invalid','true');field.focus();
  }
  form.addEventListener('input',function(event){
    if(event.target.matches('input,select,textarea'))event.target.removeAttribute('aria-invalid');
  });
  form.addEventListener('submit',function(event){
    event.preventDefault();
    var trap=form.elements.website;
    if(trap&&trap.value)return;
    status.textContent='';status.classList.remove('error');
    var checks=[
      ['name','Please enter your full name.'],
      ['email','Please enter the email address used at checkout.'],
      ['company','Please enter your company name.'],
      ['role','Please enter your role.'],
      ['teamSize','Please select your approximate team size.'],
      ['workStates','Please enter the work state or states involved.'],
      ['issueType','Please select the primary issue.'],
      ['timeline','Please select when you need to act.'],
      ['summary','Please give us a high-level summary of the situation.'],
      ['outcome','Please tell us what a useful outcome would look like.']
    ];
    for(var i=0;i<checks.length;i++){
      var field=form.elements[checks[i][0]];
      if(!field.value.trim()){showError(field,checks[i][1]);return;}
    }
    if(!form.elements.email.validity.valid){showError(form.elements.email,'Please enter a valid email address.');return;}
    if(!form.elements.safeToSubmit.checked){showError(form.elements.safeToSubmit,'Please confirm that sensitive details have been left out.');return;}

    button.disabled=true;button.textContent='Submitting…';
    var name=form.elements.name.value.trim();
    var parts=name.split(/\s+/);
    var lastName=parts.length>1?parts.pop():parts[0];
    var firstName=parts.length>1?parts.join(' '):(parts.length===1&&parts[0]!==lastName?parts[0]:'');
    var description=[
      'HR FIRE DRILL — PAID INTAKE',
      'Role: '+form.elements.role.value.trim(),
      'Approximate team size: '+form.elements.teamSize.value,
      'Work state(s): '+form.elements.workStates.value.trim(),
      'Primary issue: '+form.elements.issueType.value,
      'Action timeline: '+form.elements.timeline.value,
      '',
      'High-level situation:',
      form.elements.summary.value.trim(),
      '',
      'Desired outcome:',
      form.elements.outcome.value.trim()
    ].join('\n');
    var data=new FormData();
    data.append('xnQsjsdp','2aca8732aae656acfcae029c9788120279dd249885b72e208381c746fb2df0b5');
    data.append('zc_gad','');data.append('xmIwtLD','90334662aaad9766a77f35fd9c1cae3690b70187f9b69263e1bc254ad267fe81e987ad2ff0515dca1b24c559c09d13cb');
    data.append('actionType','TGVhZHM=');data.append('returnURL','null');data.append('ldeskuid','');data.append('LDTuvid','');data.append('aG9uZXlwb3Q','');
    data.append('First Name',firstName);data.append('Last Name',lastName);
    data.append('Email',form.elements.email.value.trim());data.append('Company',form.elements.company.value.trim());
    data.append('Lead Source','Website – HR Fire Drill (Paid)');
    data.append('Description',description);

    fetch('https://crm.zoho.com/crm/WebToLeadForm',{method:'POST',body:data,cache:'no-cache',mode:'no-cors'}).then(function(){
      if(window.valuedHRTrack)window.valuedHRTrack('hr_fire_drill_intake_submit',{issue_type:form.elements.issueType.value,timeline:form.elements.timeline.value});
      form.hidden=true;confirmation.hidden=false;confirmation.focus();
      window.scrollTo({top:Math.max(0,confirmation.getBoundingClientRect().top+window.scrollY-32),behavior:'smooth'});
    }).catch(function(){
      button.disabled=false;button.textContent='Submit Intake & Continue';
      status.textContent='We could not submit your intake. Please try again, or email admin@valuedhr.com for help.';
      status.classList.add('error');
      if(window.valuedHRTrack)window.valuedHRTrack('hr_fire_drill_intake_error');
    });
  });
})();
