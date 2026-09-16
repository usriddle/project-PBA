export const MAX_FILE_SIZE = 10 * 1024 * 1024;
export const ALLOW_FILE_TYPES = [
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp"
];
export function validatePdf(file){
    if(!file){
        return {
            "code":-1,
            "message": "파일을 먼저 선택해주세요."
        };
    }
    else if(!ALLOW_FILE_TYPES.includes(file.type)){
        return {
            "code":-1,
            "message": "지원되는 파일 유형은 다음과 같습니다. pdf, png, jpg, jpeg, webp"
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