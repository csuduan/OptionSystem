import axios from 'axios';

let base = '';



export const getUserList = params => {
  return axios.get(`${base}/user/list`, {params: params});
};

export const getUserListPage = params => {
  return axios.get(`${base}/user/listpage`, {params: params});
};

export const removeUser = params => {
  return axios.get(`${base}/user/remove`, {params: params});
};

export const batchRemoveUser = params => {
  return axios.get(`${base}/user/batchremove`, {params: params});
};

export const editUser = params => {
  return axios.get(`${base}/user/edit`, {params: params});
};

export const addUser = params => {
  return axios.get(`${base}/user/add`, {params: params});
};


export const getTradeListPage = params => {
  return axios.get(`/api/trade/listpage`, {params: params});
};

export const getEnquiryListPage = params => {
  return axios.get(`/api/enquiry/listpage`, {params: params});
};

export const editTrade = params => {
  return axios.post(`/api/editTrade`, {params: params});
};

export const getSettingList = params => {
  return axios.get(`/api/setting/list`, {params: params});
};

export const editSetting = params => {
  return axios.post(`/api/editSetting`, {params: params});
};

export const enquiry = params => {
  return axios.post(`/api/enquiry`, params);
};

export const trade = params => {
  return axios.post(`/api/trade`, params);
};

export const requestLogin = params => {
  return axios.post(`/api/adminlogin`, {params: params});
};


export const updatePwd = params => {
  return axios.post(`/api/updatePwd`, {params: params});
};


export const getCustomListPage = params => {
  return axios.get(`/api/custom/list`, {params: params});
};

export const editCustom = params => {
  return axios.post(`/api/custom/edit`, {params: params});
};
export const delCustom = params => {
  return axios.post(`/api/custom/del`, {params: params});
};



