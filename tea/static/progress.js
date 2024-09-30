$(document).ready(function() {
    let progressInterval;
    function updateProgress() {
        $.get('/tea/job-status/' + encodeURIComponent(jobId))
            .done(function(data) {
                if (data.status === 'finished') {
                    $('#progress-bar').css('width', '100%').attr('aria-valuenow', 100).text('100%');
                    $('#result-message').text('Processing complete, zip available for download').show();
                    $('#download-button').removeClass('disabled'); 
                    $('#download-button').attr('href', '/tea/download/' + encodeURIComponent(data.result)).show();
                    $('#home-button').attr('href', '/tea/').show();
                    $('#cancel-button').attr('disabled', true);
         
                    clearInterval(progressInterval);
                } else if (data.status === 'started') {
                    $('#download-button').addClass('disabled');
                    $('#progress-bar').css('width', data.progress + '%').attr('aria-valuenow', data.progress).text(Math.round(data.progress) + '%');
                } else if (data.status === 'queued' || data.status === 'failed') {
                    $('#progress-bar').css('width', '0%').attr('aria-valuenow', 0).text('0%');
                    if (data.status === 'failed') {
                        $('#error-message').text('Task failed. Please try again.').show();
                    }
                }
            })
            .fail(function(jqXHR, textStatus, errorThrown) {
                console.error("Error fetching job status:", textStatus, errorThrown);
            });
    }

    progressInterval = setInterval(updateProgress, 1000);

    $('#cancel-form').on('submit', function(event) {
        event.preventDefault();
        $.post('/tea/cancel-job/' + jobId)
            .done(function(data) {
                if (data.status === 'canceled') {
                    $('#progress-bar').css('width', '0%').attr('aria-valuenow', 0).text('Canceled');
                    $('#cancel-button').attr('disabled', true);
                    clearInterval(progressInterval);
                    setTimeout(function() {window.location.href = '/tea/';}, 1000);
                } else {
                    $('#error-message').text('Unable to cancel task.').show();
                }
            })
            .fail(function(jqXHR, textStatus, errorThrown) {
                console.error("Error canceling job:", textStatus, errorThrown);
            });
    });
});