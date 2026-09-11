import axios from "axios";
import {API_BASE_URL} from "../config/config"

export async function requestSummary(file){
    const formData= new FormData();
    formData.append("file",file)
    const response = await axios.post(`${API_BASE_URL}/api/v1/pdf/summary`,formData)
    return response;
}