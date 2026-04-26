export const sendNotification = (content: string) => {
    const n = new Notification('ezAutoPC', {
        body: content,
        tag: 'ezautopc-ai-notification',
        icon: '/favicon.png'
    });

    n.onclick = () => {
        window.focus();
        n.close();
    };
}