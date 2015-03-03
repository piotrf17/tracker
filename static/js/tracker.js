var timer_map = {};

function human_readable(time) {
  if (time < 60) {
    return Math.floor(time) + ' s';
  } else if (time < 3600) {
    return (time / 60.0).toFixed(1) + ' m';
  } else {
    return (time / 3600.0).toFixed(1) + ' h';
  }
}

function render_timer(timer_name) {
  timer = timer_map[timer_name];
  $('#' + timer_name + '_current').html(human_readable(timer.current));
  $('#' + timer_name + '_total').html(human_readable(timer.total + timer.current));
  $('#' + timer_name + '_budgeted').html(human_readable(timer.budgeted));
}

function start_timer(timer_name) {
  timer = timer_map[timer_name]
  timer.running = true;
  timer.start = Date.now() / 1000.0;
  timer.current = 0;
  $('#' + timer_name + '_start').prop('disabled', true);
  $('#' + timer_name + '_stop').prop('disabled', false);
  $.ajax({
    url: 'start/' + timer_name,
    success: function(data) {
      render_timer(timer_name);
    }
  });
}

function stop_timer(timer_name) {
  timer = timer_map[timer_name];
  timer.running = false;
  timer.total += timer.current;
  timer.current = 0;
  $('#' + timer_name + '_start').prop('disabled', false);
  $('#' + timer_name + '_stop').prop('disabled', true);
  $.ajax({
    url: 'stop/' + timer_name,
    success: function(data) {
      render_timer(timer_name);
    }
  });
}

function update_timers() {
  var now = Date.now() / 1000.0;
  for (timer_name in timer_map) {
    timer = timer_map[timer_name];
    if (timer.running) {
      timer.current = now - timer.start
      render_timer(timer_name);
    }
  }
}

$(document).ready(function() {
  // Collect all the timer names, and set times.
  $("[id^='timer_']").each(function() {
    timer_name = this.id.split('_')[1];
    timer_map[timer_name] = {
      current: $(this).data('current'),
      total: $(this).data('total'),
      budgeted: $(this).data('budgeted'),
      running: $(this).data('running') == "True",
      start: $(this).data('start'),
    };
    render_timer(timer_name);
  });
  setInterval(update_timers, 1000);
});
