export const MAX_FILE_SIZE = 10 * 1024 * 1024;

export function validatePdf(file){
    if(!file){
        return {
            "code":-1,
            "message": "파일을 먼저 선택해주세요."
        };
    }
    else if(file.type != "application/pdf"){
        return {
            "code":-1,
            "message": "pdf 파일을 선택해주세요. 다른 유형의 파일은 지원되지 않습니다."
        };
    }   
    else if(file.size>MAX_FILE_SIZE){
        return {
            "code":-1,
            "message": "파일이 너무 큽니다. 10MB 이하의 파일을 넣어주세요."
        };
    }
    else{
        return {
            "code":1,
            "message": "파일을 선택했습니다. \"요약 시작\" 버튼을 눌러주세요."
        };
    }
}