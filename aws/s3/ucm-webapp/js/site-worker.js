// site-worker.js
// import { myHelperFunction } from './site.js'; //
//importScripts('/js/site.js'); // <-- This loads utils.js into the worker scope

let count = 0;
let intervalId = null;

// On start
if (!intervalId) {
    intervalId = setInterval(() => {
        count++;
        //let loginHandler = new LoginHandler();
        //let jwt = loginHandler.hasCredentialJwt();
        //self.postMessage(`${count} -- Token: ${jwt}`);
        let messageContent = {
            type: 'countUpdate',
            count: count,
            timestamp: new Date().toISOString()
        };
        self.postMessage(messageContent); // Send message to main thread
    }, 1000 * 3);
}

self.onmessage = function (e) { // Handle messages sent to web worker
    //if (e.data === 'start') {
    //    if (!intervalId) {
    //        intervalId = setInterval(() => {
    //            count++;
    //            self.postMessage(count);
    //        }, 1000); // every 1 second
    //    }
    //} else if (e.data === 'stop') {
    //    clearInterval(intervalId);
    //    intervalId = null;
    //}
    console.log('SiteWorker:', e);
};