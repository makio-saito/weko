const { useState, useEffect  } = React;

const NUM_OF_RESULT = 10;
const LIMIT_PAGINATION_NUMBER = 5;
const COMPONENT_SEND_NAME = document.getElementById("component-send").value;
const SEND_RADIO_BUTTON_NAME = document.getElementById("first-radio-name").value;
const NOT_SEND_RADIO_BUTTON_NAME = document.getElementById("second-radio-name").value;
const COMPONENT_SEARCH_EMAIL_NAME = document.getElementById("component-search-email-name").value;
const SEARCH_BUTTON_NAME = document.getElementById("search-button-name").value;
const DELETE_BUTTON_NAME = document.getElementById("delete-button-name").value;
const SAVE_BUTTON_NAME = document.getElementById("save-button-name").value;
const SEND_BUTTON_NAME = document.getElementById("manual-send-name").value;
const MESSAGE_SUCCESS = document.getElementById("message-success").value;
const DUPLICATE_ERROR_MESSAGE = document.getElementById("duplicate-error-message").value;


class ComponentFeedbackMail extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
          flagSend: this.props.flagSend,
        }
        this.handleChangeSend = this.handleChangeSend.bind(this);
        this.handleChangeNotSend = this.handleChangeNotSend.bind(this);
    }

    static getDerivedStateFromProps(nextProps, prevState) {
      if (nextProps.flagSend != prevState.flagSend)
      {
        return {
          flagSend: nextProps.flagSend,
        }
      }
      return null;
    }

    handleChangeSend(event){
      this.setState({flagSend: true});
      this.props.bindingValueOfComponent("flagSend", true);
    }

    handleChangeNotSend(event){
      this.setState({flagSend: false});
      this.props.bindingValueOfComponent("flagSend", false);
    }

    render() {
        return (
          <div className="form-group style-component">
            <span className="control-label col-xs-2">{COMPONENT_SEND_NAME}</span>
            <div class="controls col-xs-10">
              <div className="form-group">
                <span><input className= "style-radioBtn" type="radio"  name="feedback_mail" value="send" checked = {this.state.flagSend ? "checked" : ""} onChange= {this.handleChangeSend}/>&nbsp;{SEND_RADIO_BUTTON_NAME}</span>
                <span  className = "margin-left"><input className= "style-radioBtn" type="radio" name="feedback_mail" value="not_send" checked = {this.state.flagSend ? "" : "checked"} onChange= {this.handleChangeNotSend}/>&nbsp;{NOT_SEND_RADIO_BUTTON_NAME}</span>
              </div>
            </div>
          </div>
        )
    }
}

class ComponentExclusionTarget extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
          listEmail: [],
          selectedId: [],
        }
        this.deleteCommand = this.deleteCommand.bind(this);
        this.searchCommand = this.searchCommand.bind(this);
        this.handleKeyPress = this.handleKeyPress.bind(this);
        this.generateSelectedBox = this.generateSelectedBox.bind(this);
        this.setWrapperRef = this.setWrapperRef.bind(this);
        this.setDeleteWrapperRef = this.setDeleteWrapperRef.bind(this);
        this.handleClickOutside = this.handleClickOutside.bind(this);
        this.handleClick = this.handleClick.bind(this);
    }

    componentDidMount(){
      document.addEventListener('mousedown', this.handleClickOutside);
      let mailData = [];
      let sendData = false;
      $.ajax({
        url: "/api/admin/get_feedback_mail",
        async: false,
        method: "GET",
        success: function (data) {
          mailData = data.data || [];
          sendData = data.is_sending_feedback || false;
        }
      })
      this.props.bindingValueOfComponent('listEmail', mailData);
      this.props.bindingValueOfComponent('flagSend', sendData);
    }

    componentWillUnmount() {
      document.removeEventListener('mousedown', this.handleClickOutside);
    }

    setWrapperRef(node) {
      this.wrapperRef = node;
    }

    setDeleteWrapperRef(node) {
      this.deleteRef = node;
    }

    static getDerivedStateFromProps(nextProps, prevState) {
      if (nextProps.listEmail != prevState.listEmail)
      {
        return {
          listEmail: nextProps.listEmail,
        }
      }
      return null;
    }

    handleClickOutside(event) {
      if (this.wrapperRef) {
        if (this.deleteRef && this.deleteRef.contains(event.target)){
        } else if (!this.wrapperRef.contains(event.target)) {
          this.setState({selectedId: []})
        }
      }
    }

    handleClick(id) {
      const selectedId = this.state.selectedId
      if (id < 0) {
        this.setState({
          selectedId: []
        });
      } else {
        if (!this.state.selectedId.includes(id)) {

          selectedId.push(id);
          this.setState({
            selectedId: selectedId
          });
        } else {
          this.setState({
            selectedId: selectedId.filter(e => e !== id)
          });
        }
      }
    }

    validateEmail(email) {
      var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
      return re.test(String(email).toLowerCase());
    }

    handleKeyPress(event){
      if (event.key =='Enter') {
        let new_email = {
          author_id: "",
          email: event.target.value.trim()
        }
        if (!this.validateEmail(new_email.email)){
          alert("Pleased input a valid email.");
        }
        else{
          if (this.props.addEmailToList(new_email)) {
            $('#custom_input_email').val('');
            $('#sltBoxListEmail').animate({
              scrollTop: $("#custom_input_email").offset().top
            }, 1000);
          }
        }
      }
    }

    generateSelectedBox(listEmail) {
      let innerHTML = [];
      for (let id in listEmail) {
        innerHTML.push(<a className={`list-group-item list-group-item-action ${this.state.selectedId.includes(id) ? 'active' : ''}`}
                        onClick={() => { this.handleClick(id) }}
                        key={id}
                        value={listEmail[id].author_id}>{listEmail[id].email}</a>);
      }
      return (
        <div ref={this.setWrapperRef} class="list-group" className="style-selected-box" id="sltBoxListEmail">
          {innerHTML}
          <input class="list-group-item list-group-item-action style-full-size"
          type ="text"
          id="custom_input_email"
          onKeyPress={(e) => this.handleKeyPress(e)}
          />
        </div>
      )
    }

    deleteCommand(event) {
      this.setState({selectedId: []})
      this.props.removeEmailFromList(this.state.selectedId);
    }

    searchCommand(){
      this.props.bindingValueOfComponent("showModalSearch", true);
    }

    render() {
        return (
            <div className="form-group style-component">
                <span className="control-label col-xs-2">{COMPONENT_SEARCH_EMAIL_NAME}</span>
                <div className="controls col-xs-10">
                    <div>
                        <ReactBootstrap.Button variant="primary" onClick={this.searchCommand}>
                            <i className = "glyphicon glyphicon-search"></i>&nbsp;{SEARCH_BUTTON_NAME}
                        </ReactBootstrap.Button>
                    </div>
                    <div className="style-full-size">
                      {this.generateSelectedBox(this.state.listEmail)}
                      <button ref={this.setDeleteWrapperRef}  className="btn btn-danger delete-button style-my-button style-deleteBtn" onClick={this.deleteCommand}>
                          <span className="glyphicon glyphicon-trash" aria-hidden="true"></span>
                          &nbsp;{DELETE_BUTTON_NAME}
                      </button>
                    </div>
                </div>
            </div>
        )
    }
}

class ModalMessageComponent extends React.Component {
  constructor(props) {
    super(props);
  }
  render(){
    return(
      <div className="alert alert-info">
          Sorry，No results.
      </div>
    )
  }
}

class TableUserEmailComponent extends React.Component {
  constructor(props){
    super(props);
    this.state = {
      listUser: this.props.listUser,
      firstRender: true,
    }
    this.generateBodyTableUser = this.generateBodyTableUser.bind(this);
    this.importEmail = this.importEmail.bind(this);
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    if (nextProps.listUser != prevState.listUser)
    {
      return {
        listUser: nextProps.listUser,
        firstRender: false,
      }
    }
    return null;
  }

  generateBodyTableUser()
  {
    let tBodyElement = this.state.listUser.map((row) =>{
      let name = "";
      if (row._source.authorNameInfo[0]){
        name = row._source.authorNameInfo[0].fullName
      }
      return (
          <tr key = {row._source.pk_id.toString()}>
            <td>{name}</td>
            <td>{row._source.emailInfo[0].email}</td>
            <td className="text-right"><button className="btn btn-info" onClick = {(event) => this.importEmail(event, row._source.pk_id, row._source.emailInfo[0].email)}>&nbsp;&nbsp;Import&nbsp;&nbsp;</button></td>
          </tr>
        )
      }
    )
    return (
      <tbody >
        {tBodyElement}
      </tbody>
    )
  }
  importEmail(event, pk_id, email){
    event.target.disabled=true;
    let data = {
      "author_id" : pk_id,
      "email" : email
    }
    this.props.addEmailToList(data);
  }
  render(){
    return (
      <div className="col-sm-12 col-md-12">
        <table className="table table-striped style-table-modal" id="table_data">
          <caption ></caption>
          <thead >
            <tr  className="success">
              <th  className="thWidth style-column">Name</th>
              <th  className="thWidth style-column">Mail Address</th>
              <th  className="alignCenter" ></th>
            </tr>
          </thead>
          {this.generateBodyTableUser()}
        </table>
        {this.state.firstRender == false && this.state.listUser.length == 0 ? <ModalMessageComponent/> : ""}
      </div>
    )
  }
}

class SearchComponent extends React.Component {
  constructor(props){
    super(props);
    this.state = {
      searchKey : this.props.searchKey,
    }
    this.searchEmail = this.searchEmail.bind(this);
    this.handleChange = this.handleChange.bind(this);
  }
  searchEmail(){
    let request = {
      searchKey: this.state.searchKey,
      pageNumber: 1,
    }
    fetch("/api/admin/search_email", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
    })
    .then(res => res.json())
    .then((result) => {
      this.props.getListUser(result.hits.hits, result.hits.total);
    });
  }
  handleChange(event){
    this.setState({ searchKey: event.target.value });
    this.props.getSearchKey(event.target.value);
    event.preventDefault();
  }
  render(){
    return (
      <div>
        <div className="col-sm-5 col-md-5">
          <input className="form-control" placeholder="" type="text" onChange={this.handleChange} value={this.state.searchKey}/>
        </div>
        <div className="col-sm-1 col-md-1">
          <button class="btn btn-primary search-button" type="button" onClick = {this.searchEmail}>&nbsp;&nbsp;
            <i class="fa fa-search-plus"></i>
            &nbsp;
            Search &nbsp;&nbsp;
          </button>
        </div>
      </div>
    )
  }
}

class Pagination extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      numOfResult: this.props.numOfResult,
      startPage: 1,
      endPage: 1,
      currentPage: 1,
      numOfPage: 1,
    }
    this.generatePagination = this.generatePagination.bind(this);
  }
  static getDerivedStateFromProps(nextProps, prevState) {
    if (nextProps.numOfResult != prevState.numOfResult)
    {
      let pageCount = nextProps.numOfResult / NUM_OF_RESULT;
      pageCount = parseInt(pageCount);
      if(nextProps.numOfResult % NUM_OF_RESULT != 0){
        pageCount += 1;
      }
      let endPage = pageCount;
      let startPage = 1;
      if (pageCount > 5)
      {
        endPage = 5;
      }
      return {
        numOfResult: nextProps.numOfResult,
        numOfPage: pageCount,
        endPage: endPage,
        startPage: startPage,
      }
    }
    return null;
  }

  locatePageResult(pageNumber){
    if(pageNumber < 1 || pageNumber > this.state.numOfPage){
      return;
    }
    let startPage = this.state.startPage;
    let endPage = this.state.endPage;
    if (this.state.numOfPage > 5 ){
      if(pageNumber > 2 && pageNumber < this.state.numOfPage -2){
        startPage = pageNumber -2 ;
        endPage = pageNumber + 2;
      }
      else {
        if(pageNumber < 3){
          startPage = 1;
          endPage = 5;
        }
        if (pageNumber > this.state.numOfPage -2){
          startPage = this.state.numOfPage - 4;
          endPage = this.state.numOfPage;
        }
      }
    }
    this.setState({
      currentPage: pageNumber,
      startPage: startPage,
      endPage:endPage
    });
    let request = {
      searchKey: this.props.searchKey,
      pageNumber: pageNumber,
    }
    fetch("/api/admin/search_email", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
    })
    .then(res => res.json())
    .then((result) => {
      this.props.getListUser(result.hits.hits, result.hits.total);
    });
  }
  generatePagination(){
    let listPage = [];
    for (let i = this.state.startPage; i <= this.state.endPage; i++){
      listPage.push(
        <li  key = {i.toString()} className = {this.state.currentPage == i ? 'active' : ''}>
          <a  href="#" onClick = {() => this.locatePageResult(i)}>{i}</a>
        </li>
      )
    }
    return (
      <ul  className="pagination">
        {this.state.numOfPage > LIMIT_PAGINATION_NUMBER ?
        <li >
          <a  href="#" onClick = {() => this.locatePageResult(1)} className = {this.state.currentPage == 1 ? 'my-pagination-disabled' : ''}><span  aria-hidden="true">&#8810;</span></a>
        </li> : null }
        <li >
          <a  href="#" onClick = {() => this.locatePageResult(this.state.currentPage - 1)} className = {this.state.currentPage == 1 ? 'my-pagination-disabled' : ''}><span  aria-hidden="true">&lt;</span></a>
        </li>
        {listPage}
        <li >
          <a  href="#" onClick = {() => this.locatePageResult(this.state.currentPage + 1)} className = {this.state.currentPage == this.state.numOfPage ? 'my-pagination-disabled' : ''}><span  aria-hidden="true">&gt;</span></a>
        </li>
        {this.state.numOfPage > LIMIT_PAGINATION_NUMBER ?
        <li >
          <a  href="#" onClick = {() => this.locatePageResult(this.state.numOfPage)} className = {this.state.currentPage == this.state.numOfPage ? 'my-pagination-disabled' : ''}><span  aria-hidden="true">&#8811;</span></a>
        </li> : null }
      </ul>
    )
  }
  render () {
    return (
      <div  className="row">
        <div  className="col-sm-12 col-md-12 text-center">
          {this.generatePagination()}
        </div>
      </div>
    )
  }
}

class ModalSearchBodyComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      listUser: [],
      numOfResult: 0,
      searchKey: "",
    }
    this.getListUser = this.getListUser.bind(this);
    this.getSearchKey = this.getSearchKey.bind(this);
  }
  getListUser(data, count)
  {
    this.setState({
      listUser: data,
      numOfResult: count
    });
  }
  getSearchKey(data){
    this.setState({searchKey:data});
  }
  render() {
    return (
      <div className="container-modal">
        <div className="row">
          <div className="col-sm-12 col-md-12 col-md-12">
            <div className="row">
              <div className="row">
                <SearchComponent getListUser = {this.getListUser} searchKey = {this.state.searchKey} getSearchKey= {this.getSearchKey}/>
              </div>
              <div className="row">
                <TableUserEmailComponent listUser = {this.state.listUser} addEmailToList={this.props.addEmailToList}/>
              </div>
              <div className = "row">
                <Pagination numOfResult = {this.state.numOfResult} searchKey = {this.state.searchKey} getListUser = {this.getListUser}/>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }
}
class ModalFooterComponent extends React.Component {
  constructor(props){
    super(props);
    this.handleClose = this.handleClose.bind(this);
  }
  handleClose() {
      this.props.bindingValueOfComponent("showModalSearch", false);
  }
  render(){
    return (
        <ReactBootstrap.Button className="btn-primary text-white" onClick={this.handleClose}>
          <span className="glyphicon glyphicon-remove text-white"></span>
          &nbsp;Close
        </ReactBootstrap.Button>
    )
  }
}

class ModalSearchComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      show: this.props.showModalSearch,
    };
  }
  static getDerivedStateFromProps(nextProps, prevState) {
    if (nextProps.showModalSearch != prevState.showModalSearch)
    {
      return {
        show: nextProps.showModalSearch,
      }
    }
    return null;
  }
  render(){
    return (
      <ReactBootstrap.Modal show={this.state.show} onHide={this.handleClose} dialogClassName="feedback-mail-modal">
        <ReactBootstrap.Modal.Body className="feedback-mail-modal-body">
          <ModalSearchBodyComponent addEmailToList = {this.props.addEmailToList}/>
        </ReactBootstrap.Modal.Body>
        <ReactBootstrap.Modal.Footer>
          <ModalFooterComponent bindingValueOfComponent = {this.props.bindingValueOfComponent} modal = "modalSearch"/>
        </ReactBootstrap.Modal.Footer>
      </ReactBootstrap.Modal>
    )
  }
}

const ModalFooterResendComponent = function(props){
  function handleClose() {
    props.bindingValueOfComponent("showModalResend", false);
  }
  function handleSend(){
    addAlert("Mail Sending...", 2);
    let id = "" + props.bindID;
    let request = {
      'history_id': id
    };
    $.ajax({
      url: "/api/admin/resend_failed_mail",
      method: "POST",
      headers: {
        'Content-Type': 'application/json'
      },
      data: JSON.stringify(request),
      dataType: "json",
      success: function (data, status) {
        closeAlert();
      },
      error: function (data, status) {
        closeAlert();
        addAlert("Failed to resend email.", 1);
      }
    });
    props.bindingValueOfComponent("showModalResend", false);
    props.bindingValueOfComponent("resendMail", true);
  }
  return (
    <div>
      <ReactBootstrap.Button className="btn-success text-white left-align" onClick={() => handleSend()}>
        <span className="glyphicon glyphicon-send text-white"></span>
        &nbsp;Resend
      </ReactBootstrap.Button>
      <ReactBootstrap.Button className="btn-primary text-white" onClick={() => handleClose()}>
        <span className="glyphicon glyphicon-remove text-white"></span>
        &nbsp;Close
      </ReactBootstrap.Button>
    </div>
  )
}

const TableResendErrorComponent = function(props){
  const [data, setData] = useState([]);
  const [numOfPage, setNumOfPage] = useState(1);
  const [currentIndex, setIndex] = useState(0);

  useEffect(() => {
    fetch("/api/admin/get_failed_mail?page=1&id="+ props.bindID)
    .then(res => res.json())
    .then(
      (result) => {
        if (result.error) {
          alert(result.error);
          return;
        }
        setNumOfPage(result.total_page);
        setData(result.data);
      },

      (error) => {
        console.log(error);
      }
    );
  },[]);

  function getData(data){
    setData(data.data);
    setIndex(data.selected_page-1);
    setNumOfPage(data.total_page);
  }

  function generateBodyTableUser(){
    let listRow = data.map((rowData, index) =>
    <tr>
      <td>{(currentIndex * 10) + index+1}</td>
      <td>{rowData.name}</td>
      <td>{rowData.mail}</td>
    </tr>);
    return(
      <tbody>
        {listRow}
      </tbody>
    )
  }
  return (
    <div>
      <table class="table table-striped resend-mail-table">
        <thead>
          <tr>
            <th className = "width-small">#</th>
            <th className = "width-long">Name</th>
            <th>Mail Address</th>
          </tr>
        </thead>
        {generateBodyTableUser()}
      </table>
      <div className = "row">
        <PaginationResendLogsTable bindURL = "/api/admin/get_failed_mail" bindID = {props.bindID} bindNumOfPage = {numOfPage} bindGetData = {getData}/>
      </div>
    </div>
  )
}

const PaginationResendLogsTable = function(props){
  const[numOfPage, setNumOfPage] = useState(props.bindNumOfPage);
  const[startPage, setStartPage] = useState(1);
  const[endPage, setEndPage] = useState(1);
  const[currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    setNumOfPage(props.bindNumOfPage);
    if(props.bindNumOfPage > 5){
      setEndPage(5);
    }
    else{
      setEndPage(props.bindNumOfPage);
    }
  }, [props.bindNumOfPage]);

  function locatePageResult(pageNumber){
    if(pageNumber < 1 || pageNumber > numOfPage){
      return;
    }
    if (numOfPage > 5 ){
      if(pageNumber > 2 && pageNumber < numOfPage -2){
        setEndPage(pageNumber + 2);
        setStartPage(pageNumber -2);
      }
      else {
        if(pageNumber < 3){
          setStartPage(1);
          setEndPage(5);
        }
        if (pageNumber >numOfPage -2){
          setStartPage(numOfPage - 4);
          setEndPage(numOfPage);
        }
      }
    }
    setCurrentPage(pageNumber);
    let extendData = "";
    if(props.bindID){
      extendData +="&id=" + props.bindID;
    }
    fetch(props.bindURL + "?page=" + pageNumber + extendData)
    .then(res => res.json())
    .then((result) => {
      if (result.error) {
        alter(result.error);
        return;
      }
      props.bindGetData(result);
    });
    (error) => {
      console.log(error);
    }
  }

  function generatePagination(){
    let listPage = [];
    for (let i = startPage; i <= endPage; i++){
      listPage.push(
        <li  key = {i.toString()} className = {currentPage == i ? 'active' : ''}>
          <a  href="#" onClick = {() => locatePageResult(i)}>{i}</a>
        </li>
      )
    }
    return (
      <ul  className="pagination">
        {numOfPage > LIMIT_PAGINATION_NUMBER ?
        <li >
          <a  href="#" onClick = {() => locatePageResult(1)} className = {currentPage == 1 ? 'my-pagination-disabled' : ''}><span  aria-hidden="true">&#8810;</span></a>
        </li> : null }
        <li >
          <a  href="#" onClick = {() => locatePageResult(currentPage - 1)} className = {currentPage == 1 ? 'my-pagination-disabled' : ''}><span  aria-hidden="true">&lt;</span></a>
        </li>
        {listPage}
        <li >
          <a  href="#" onClick = {() => locatePageResult(currentPage + 1)} className = {currentPage == numOfPage ? 'my-pagination-disabled' : ''}><span  aria-hidden="true">&gt;</span></a>
        </li>
        {numOfPage > LIMIT_PAGINATION_NUMBER ?
        <li >
          <a  href="#" onClick = {() => locatePageResult(numOfPage)} className = {currentPage == numOfPage ? 'my-pagination-disabled' : ''}><span  aria-hidden="true">&#8811;</span></a>
        </li> : null }
      </ul>
    )
  }
  return(
    <div  className="row">
      <div  className="col-sm-12 col-md-12 text-center">
        {generatePagination()}
      </div>
    </div>
  )
}

const ModalResendBodyComponent = function(props) {
  return (
    <div>
      <div className = "row">
        <label className="label-resend-email">List of authors who failed to send</label>
      </div>
      <div className = "row">
        <TableResendErrorComponent bindID = {props.bindID}/>
      </div>
    </div>
  )
}

const ModalResendComponent = function(props){
  const [showModal, setShowModal] = useState(props.showModalResend)

  useEffect(() => {
    setShowModal(props.showModalResend);
  }, [props.showModalResend])

  function handleClose() {
    this.props.bindingValueOfComponent("showModalResend", false);
  }

  return (
    <ReactBootstrap.Modal show={showModal} onHide={() => handleClose()} dialogClassName="resend-mail-modal">
      <ReactBootstrap.Modal.Body className="feedback-mail-modal-body">
        <ModalResendBodyComponent bindID = {props.bindID}/>
      </ReactBootstrap.Modal.Body>
      <ReactBootstrap.Modal.Footer>
        <ModalFooterResendComponent bindingValueOfComponent = {props.bindingValueOfComponent} bindID = {props.bindID}/>
      </ReactBootstrap.Modal.Footer>
    </ReactBootstrap.Modal>
  )
}

class ComponentButtonLayout extends React.Component {
    constructor(props) {
        super(props);
        this.saveCommand = this.saveCommand.bind(this);
    }

    saveCommand(event) {
      let is_sending_feedback = this.props.flagSend;
      let request_param = {
        "data": this.props.listEmail,
        "is_sending_feedback": is_sending_feedback
      }

      fetch(
        "/api/admin/update_feedback_mail",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(request_param)
        }
      )
      .then(res => res.json())
      .then((result) => {
        let message = MESSAGE_SUCCESS;
        let type = 0;
        if (!result.success) {
          message = result.error;
          type = 1;
        }
        else{
          props.bindingValueOfComponent("resendMail", true);
        }

        addAlert(message, type);
      });
    }

    render() {
      return (
        <div className="form-group style-component ">
          <div className="col-xs-5">
            <button className="btn btn-primary style-button" onClick={this.saveCommand}>
              <span className="glyphicon glyphicon-saved"></span>
              &nbsp;
              {SAVE_BUTTON_NAME}
            </button>
          </div>
        </div>
      )

    }
}

const ComponentLogsTable = function(props){
  const [data, setData] = useState([]);
  const [numOfPage, setNumOfPage] = useState(1);
  const [currentIndex, setIndex] = useState(0);

  function showErrorMail(id){
    props.bindingValueOfComponent("showModalResend", true)
    props.bindingValueOfComponent("mailId", id);
  }

  useEffect(() => {
    fetch("/api/admin/get_send_mail_history?page=1")
    .then(res => res.json())
    .then(
      (result) => {
        if (result.error) {
          alert(result.error);
          return;
        }
        setNumOfPage(result.total_page);
        setData(result.data);
      },

      (error) => {
        console.log(error);
      }
    );
  }, []);

  useEffect(() => {
    fetch("/api/admin/get_send_mail_history?page=1")
    .then(res => res.json())
    .then(
      (result) => {
        if (result.error) {
          alert(result.error);
          return;
        }
        setNumOfPage(result.total_page);
        setData(result.data);
      },

      (error) => {
        console.log(error);
      }
    );
    props.bindingValueOfComponent("resendMail", false);
  }, [props.bindResendMail]);

  function getData(data){
    setData(data.data);
    setIndex(data.selected_page-1);
  }

  function generateTableBody() {
    let listRow = data.map((rowData, index) => {
      let error = rowData.error;
      if (rowData.error != '0' && rowData.is_latest) {
        error = <a data-id={rowData.id} href="#" onClick = {() => showErrorMail(rowData.id)}>{rowData.error}</a>
      }
      return (
        <tr key={rowData.id}>
          <td>{(currentIndex * 10) + index + 1}</td>
          <td>{rowData.start_time}</td>
          <td>{rowData.end_time}</td>
          <td>{rowData.count}</td>
          <td>{rowData.success}</td>
          <td>{error}</td>
        </tr>
      )
    }
    );
    return (
      <tbody>
        {listRow}
      </tbody>
    )
  }

  return (
    <div className = "form-group style-component">
      <div className="control-label col-xs-2">Send logs</div>
      <br/>
      {!data ? <div>There is no data.</div> : null}
      <table class="table table-striped style-table-send-logs">
        <thead>
          <tr>
            <th className = "width-small">#</th>
            <th className = "width-long">Start Time</th>
            <th className = "width-long">End Time</th>
            <th className = "width-medium">Counts</th>
            <th className = "width-medium">Success</th>
            <th className = "width-medium">Error</th>
          </tr>
        </thead>
        {generateTableBody()}
      </table>
      {data ?
      <div className = "row">
        <PaginationResendLogsTable bindURL="/api/admin/get_send_mail_history" bindNumOfPage = {numOfPage} bindGetData = {getData}/>
      </div> : null}
    </div>
  )
}

class MainLayout extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
          showModalSearch: false,
          showModalResend: false,
          listEmail: [],
          flagSend: false,
          mailId: "",
          resendMail: false
        }
        this.bindingValueOfComponent = this.bindingValueOfComponent.bind(this);
        this.addEmailToList = this.addEmailToList.bind(this);
        this.removeEmailFromList = this.removeEmailFromList.bind(this);
    }
    bindingValueOfComponent (key, value) {
      switch (key) {
        case "showModalSearch":
          this.setState({showModalSearch: value});
          break;
        case "listEmail":
            this.setState({listEmail: value});
            break;
        case "flagSend":
            this.setState({flagSend: value});
            break;
        case "showModalResend":
          this.setState({showModalResend: value})
          break;
        case "mailId":
            this.setState({mailId: value})
            break;
        case "resendMail":
            this.setState({resendMail: value})
            break;
      }
    }
    addEmailToList(data){
      let listUser = [];
      $("#sltBoxListEmail > a").each(function(){
        listUser.push(this.text);
      });
      let isExist = listUser.includes(data.email);
      if(isExist){
        alert(DUPLICATE_ERROR_MESSAGE);
        return false;
      }
      let listEmail = this.state.listEmail;
      listEmail.push(data);
      this.setState({listEmail: listEmail})
      return true;
    }
    removeEmailFromList(listData){
      listData.sort();
      let listEmail = this.state.listEmail;
      for (var i = listData.length -1; i >= 0; i--){
        listEmail.splice(listData[i],1);
      }
      this.setState({listEmail: listEmail});
    }
    render() {
        return (
            <div>
                <div id="alerts"></div>
                <div className="row">
                  <ComponentFeedbackMail flagSend = {this.state.flagSend} bindingValueOfComponent = {this.bindingValueOfComponent}/>
                </div>
                <div className="row">
                  <ComponentExclusionTarget bindingValueOfComponent = {this.bindingValueOfComponent} removeEmailFromList = {this.removeEmailFromList} listEmail={this.state.listEmail} addEmailToList= {this.addEmailToList}/>
                </div>
                <div className = "row">
                  <ComponentLogsTable bindingValueOfComponent = {this.bindingValueOfComponent} bindResendMail = {this.state.resendMail}/>
                </div>
                <div className="row">
                  <ComponentButtonLayout listEmail = {this.state.listEmail} flagSend={this.state.flagSend}/>
                </div>
                <div className="row">
                  <ModalSearchComponent showModalSearch = {this.state.showModalSearch} bindingValueOfComponent = {this.bindingValueOfComponent} addEmailToList={this.addEmailToList}/>
                </div>
                <div className = "row">
                  <ModalResendComponent showModalResend = {this.state.showModalResend} bindingValueOfComponent = {this.bindingValueOfComponent} bindID = {this.state.mailId}/>
                </div>
            </div>
        )
    }
}

$(function () {
    ReactDOM.render(
        <MainLayout/>,
        document.getElementById('root')
    )
});

function addAlert(message, type) {
  let className = "alert alert-success alert-boder";
  let closeButton = '<button type="button" class="close" data-dismiss="alert">&times;</button>'
  if(type==1){
    className = "alert alert-danger alert-dismissable alert-boder";
  }
  if(type==2){
    className = "alert alert-info alert-dismissable alert-boder";
    closeButton = "";
  }
  $('#alerts').append(
    '<div class="' + className + '">'
    + closeButton + message + '</div>');
}

function closeAlert(){
  $('#alerts').empty();
}
