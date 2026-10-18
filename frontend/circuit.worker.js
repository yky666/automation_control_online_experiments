import {simulateCircuit} from './circuits.js';
self.onmessage=event=>{try{self.postMessage({result:simulateCircuit(event.data)})}catch(error){self.postMessage({error:error.message})}};
