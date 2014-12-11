;

(function ($) {

  function incrementFields(form, formset) {
    var $inputs = $(':input', form)
      , oldCounter
      , newCounter

    newCounter = 1 + Math.max.apply(Math, $(':input', formset).map(function () {
      return (/\d+/).exec(this.name);
    }));

    oldCounter = parseInt($inputs
        .attr('name')
        .match(/\d+/)[0], 10);

    $inputs.each(function () {
      var $this = $(this);
      if ($this.attr('name')) {
        $this.attr('name', $this.attr('name').replace(oldCounter, newCounter));
      }
      if ($this.attr('id')) {
        $this.attr('id', $this.attr('id').replace(oldCounter, newCounter));
      }
    });
  }

  function updateFields(selector, data) {
    var $container = $(selector);
    $.each(data, function(key, val) {
      $container.find(':input[name$="' + key + '"]').val(val);
    });
  }

  $.fn.appendFormset = function (selector, data) {
    return this.each(function () {
      var $formset = $(this)
        , items = $(selector, $formset)
        , lastForm
        , newForm

      lastForm = items.filter(':hidden').length ?
        items.filter(':hidden').last() :
        items.last();

      newForm = lastForm.clone();

      if (lastForm.is(':hidden')) {
        newForm.insertBefore(lastForm);
      } else {
        newForm.insertAfter(lastForm);
      }
      
      incrementFields(newForm, this);
      updateFields(newForm, data || {});

      newForm
        .find('input[name$="-id"]').remove();

      $('input[name$="TOTAL_FORMS"]', $formset)
        .val($(selector, $formset).length);

      $formset
        .trigger('formsetAppended', newForm, lastForm)
        .trigger('formsetUpdated', newForm);
      
    });
  }

})($);

$(document).ready(function () {

  $('form')
    // Warn users who have not saved changes before leaving page
   // .one('change', function () { //CENDARI : remove anoying messages
      //window.onbeforeunload = function () {
     //   return 'You have unsaved changes.';
     // };
   // })
    // ..but not when next page is triggered by clicking save
    .on('submit', function () {
      window.onbeforeunload = null;
    })

    // Allow fields to be collapsed to save space
    .on('click', '.collapsable legend', function () {
      var $this = $(this);
      $this.toggleClass('.collapsed')
        .find('i').toggleClass('fa-plus fa-minus');
      $this.siblings('.fieldset-content').toggle();
    })

    // When icon to remove topic is clicked, check the corresponding
    // 'DELETE' checkbox & hide the item.
    .on('click', '.remove-related-topic', function (event) {
      event.preventDefault();
      $(this)
        .siblings('input[name$="DELETE"]').attr('checked', true)
        .parents('.topicassignment').fadeOut('slow');
    });


  // Add icons for fieldset collapsing & trigger click on fields to be
  // hidden by default
  $('.collapsable legend')
    .css('cursor', 'pointer')
    .each(function () {
      $('<i>', {
        'class': 'fa fa-minus',
        'css': {'margin': '6px 0 0 3px'}
      }).appendTo(this);
    })
    .filter('.collapse-on-show').trigger('click');

  $('.related-topics input[name$="DELETE"]').each(function () {
    var $this = $(this);

    $this.closest('.control-group').replaceWith($this);

    $('<a>', {
      'class': 'remove-related-topic',
      'href': '#',
      'html': '<i class="fa fa-times-circle"></i>'
    }).appendTo($(this).hide().parents('.topicassignment'));
  });

  $('<input type="text" placeholder="Add topic (type to search)">')
    .on('change input', function (event) {
      // Don't trigger change or input events when typing into this field,
      // since it's just used for autocomplete & won't be saved
      event.stopPropagation();
    })
    .appendTo('.related-topics .fieldset-content')
    .after($('<img>', {
      id: 'related-topics-loading',
      src: '/static/style/icons/ajax-loader.gif',
      css: {'margin-left': '4px', 'display': 'none'}
    }))
    .autocomplete({
      source: function (request, response) {
        $.ajax({
          url: '/api' + window.location.pathname.match(/^\/projects\/[^/]+/)[0] + '/topics/',
          dataType: 'json',
          data: {'q': request.term},
          beforeSend: function () {
            $('#related-topics-loading').css('display', 'inline-block');
          },
          success: function (data) {
            response($.map(data.results, function (item, index) {
              return { id: item.id, label: item.preferred_name, uri: item.uri };
            }));
          },
          complete: function () {
            $('#related-topics-loading').hide();
          }
        });
      },
      minLength: 2,
      position: {
        my: 'left bottom',
        at: 'left top'
      },
      select: function (event, ui) {
        var $oldExtraField = $('.related-topics .topicassignment:last').trigger('change')
          , $newExtraField = $oldExtraField.clone().insertAfter($oldExtraField)
          , oldFieldCounter
          , newFieldCounter

        // Create a new extra field
        oldFieldCounter = parseInt($oldExtraField
          .find('input[type="hidden"]')
          .attr('name')
          .match(/\d+/)[0], 10);

        newFieldCounter = oldFieldCounter + 1;

        $newExtraField.find('input').each(function () {
          var $this = $(this);
          if ($this.attr('name')) {
            $this.attr('name', $this.attr('name').replace(oldFieldCounter, newFieldCounter));
          }
          if ($this.attr('id')) {
            $this.attr('id', $this.attr('id').replace(oldFieldCounter, newFieldCounter));
          }
        });

        // Update management form to reflect new number of fields
        $oldExtraField
          .parents('fieldset')
          .find('input[name$=TOTAL_FORMS]')
            .val(newFieldCounter + 1);

        // Replace this input with a text field
        $oldExtraField
          .prepend(ui.item.label)
          .find('input[name$="topic_id"]').val(ui.item.id);

        // Clear this input
        event.preventDefault();
        $(this).val('').blur();

      }
    });

});
