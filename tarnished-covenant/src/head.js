
(function(){
  var standalone = window.navigator.standalone === true;
  try { standalone = standalone || window.matchMedia('(display-mode: standalone)').matches; } catch (_) {}
  if (standalone) document.documentElement.classList.add('tc-standalone');
})();
