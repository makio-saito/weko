require([
  "jquery",
  "bootstrap"
], function () {
  data_global = {
    post_uri: '',
    post_data: {}
  }

  // click button Next
  $('#btn-finish').on('click', function () {
    if(preparePostData(0)){
      sendQuitAction();
    }
  });

  // click button Save
  $('#btn-draft').on('click', function () {
    preparePostData(1);
    sendQuitAction();
  });

  // click button Continue
  $('#btn_withdraw_continue').on('click', function () {
    sendWithdrawAction();
  });

  // click button Withdraw
  $('#btn_withdraw').on('click', function () {
    $('#action_withdraw_confirmation').modal('show');
  });

  $('#lnk_item_detail').on('click', function () {
    $('#myModal').modal('show');
  });

  $('button#btn_close_alert').on('click', function () {
    $('#pwd').parent().removeClass('has-error');
    $('#error-info').parent().hide();
  });

  // prepare data for sending
  function preparePostData(tmp_save) {
    let isSuffixFormat = true;

    data_global.post_uri = $('.cur_step').data('next-uri');

    let identifier_grant = $("input[name='identifier_grant']:checked").val();
    let identifier_grant_jalc_doi_suffix = getVal($("input[name='idf_grant_input_1']"));
    let identifier_grant_jalc_doi_link = $("span[name='idf_grant_link_1']").text() + getVal($("input[name='idf_grant_input_1']"));
    let identifier_grant_jalc_cr_doi_suffix = getVal($("input[name='idf_grant_input_2']"));
    let identifier_grant_jalc_cr_doi_link = $("span[name='idf_grant_link_2']").text() + getVal($("input[name='idf_grant_input_2']"));
    let identifier_grant_jalc_dc_doi_suffix = getVal($("input[name='idf_grant_input_3']"));
    let identifier_grant_jalc_dc_doi_link = $("span[name='idf_grant_link_3']").text() + getVal($("input[name='idf_grant_input_3']"));
    let identifier_grant_crni_link = $("span[name='idf_grant_link_4']").text();

    data_global.post_data = {
      identifier_grant: identifier_grant,
      identifier_grant_jalc_doi_suffix: identifier_grant_jalc_doi_suffix,
      identifier_grant_jalc_doi_link: identifier_grant_jalc_doi_link,
      identifier_grant_jalc_cr_doi_suffix: identifier_grant_jalc_cr_doi_suffix,
      identifier_grant_jalc_cr_doi_link: identifier_grant_jalc_cr_doi_link,
      identifier_grant_jalc_dc_doi_suffix: identifier_grant_jalc_dc_doi_suffix,
      identifier_grant_jalc_dc_doi_link: identifier_grant_jalc_dc_doi_link,
      identifier_grant_crni_link: identifier_grant_crni_link,
      action_version: $('.cur_step').data('action-version'),
      commond: '',
      temporary_save: tmp_save
    };

    switch(identifier_grant) {
      case "0":
        break;
      case "1":
        isSuffixFormat = isDOISuffixFormat(identifier_grant_jalc_doi_link, identifier_grant_jalc_doi_suffix);
        break;
      case "2":
        isSuffixFormat = isDOISuffixFormat(identifier_grant_jalc_cr_doi_link, identifier_grant_jalc_cr_doi_suffix);
        break;
      case "3":
        isSuffixFormat = isDOISuffixFormat(identifier_grant_jalc_dc_doi_link, identifier_grant_jalc_dc_doi_suffix);
        break;
      case "4":
        break;
      default:
        break;
    };
    
    return isSuffixFormat;
  }

  function isDOISuffixFormat(doi_link, doi_suffix){
    
    let regexDOI = /^[_\-.;()\/A-Za-z0-9]+$/gi;
    
    if(doi_suffix == "" || doi_suffix == null) {
        alert("DOI is not input");
        return false;
    };
    
    if(!regexDOI.test(doi_suffix)) {
        alert("It's able to input only haft-width alphanumeric or half-width symbol _-.;()/");
        return false;
    };

    if(doi_link.length >= 300) {
        alert("Input value exceeds 300 characters");
        return false;
    };
    
    if(isExistDOI(doi_link)) {
        alert("This DOI has been used already for another item. Please input another DOI");
        return false;
    };

//    if(isWithDrawDOI(doi_link)) {
//    };


    
    return true;
  }

  function getVal(inObject) {
    val = inObject.val();
    if (val === undefined) {
      return '';
    } else {
      return val;
    }
  }

  // send
  function sendQuitAction() {
    $.ajax({
      url: data_global.post_uri,
      method: 'POST',
      async: true,
      contentType: 'application/json',
      data: JSON.stringify(data_global.post_data),
      success: function (data, status) {
        if (0 == data.code) {
          if (data.hasOwnProperty('data') && data.data.hasOwnProperty('redirect')) {
            document.location.href = data.data.redirect;
          } else {
            document.location.reload(true);
          }
        } else {
          alert(data.msg);
        }
      },
      error: function (jqXHE, status) {
        alert('Server error');
        $('#myModal').modal('hide');
      }
    });
  }
  
  function isExistDOI(doi_link){
    debugger;
    let getUrl = '/workflow/findDOI';
    let data = {'doi_link': doi_link};
    let isExistDOI = false;
    $.ajax({
        type: 'POST',
        url: getUrl,
        contentType: 'application/json; charset=UTF-8',
        async: false,
        data: JSON.stringify(data),
        dataType: "json",
        success: function (data, status) {
        debugger;
        if (0 == data.code) {
            isExistDOI = data.isExistDOI;
        } else {
            alert('Server error');
            $('#pwd').parent().addClass('has-error');
            $('#error-info').html(data.msg);
            $('#error-info').parent().show();
        }
      },
      error: function (jqXHE, status) {
        alert('Server error');
      }
    });
    
    return isExistDOI;
  }
  
  function sendWithdrawAction() {
    let form = $('form[name$=withdraw_doi_form]');
    let withdraw_uri = form.attr('action');
    let post_data = {passwd: $('#pwd').val()};
    $.ajax({
      url: withdraw_uri,
      method: 'POST',
      async: true,
      contentType: 'application/json',
      data: JSON.stringify(post_data),
      success: function (data, status) {
        if (0 == data.code) {
          if (data.hasOwnProperty('data') && data.data.hasOwnProperty('redirect')) {
            document.location.href = data.data.redirect;
          } else {
            document.location.reload(true);
          }
        } else {
          $('#pwd').parent().addClass('has-error');
          $('#error-info').html(data.msg);
          $('#error-info').parent().show();
        }
      },
      error: function (jqXHE, status) {
        alert('Server error');
      }
    });
  }
})
