import axios from "axios";
import {API_BASE_URL} from "../config/config"

export async function reqeustSummary(file){
    const formData= new FormData();
    formData.append("file",file)
    const response = await axios.post(`${API_BASE_URL}/api/v1/pdf/summary`,formData)
    if(response.status !=200){
        throw new Error(`HTTP ${response.status}`);
    }
    return response;
}