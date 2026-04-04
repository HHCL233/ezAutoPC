export function isDictionary(obj: any) {
    return Object.prototype.toString.call(obj) === '[object Object]';
}