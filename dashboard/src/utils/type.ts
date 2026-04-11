export function isDictionary(obj: any, strict?: boolean) {
    if (strict) {
        return Object.prototype.toString.call(obj) === '[object Object]';
    } else {
        return typeof obj == "object";
    }
}