export function html(strings, ...values) {
    return strings.reduce((result, str, i) => {
        const value = values[i] !== undefined ? values[i] : "";
        return result + str + value;
    }, "");
}

export const websocketUrl = `ws${window.location.protocol === "https:" ? "s" : ""}://${window.location.host}/websocket`