// site-worker.js

let count = 0;
let intervalId = null;

// On start
if (!intervalId) {
    intervalId = setInterval(() => {
        count++;
        self.postMessage(count);
    }, 1000 * 60 * 15);
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