$(".tabber-menu-item").on('click', function() {
  $(".tabber-menu-item").removeClass('active');
  $(this).addClass('active')
});