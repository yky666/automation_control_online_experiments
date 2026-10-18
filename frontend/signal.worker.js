import {simulateSignal} from './signal-solver.js';
self.onmessage=e=>{try{self.postMessage({result:simulateSignal(e.data.graph,e.data.request,e.data.example)})}catch(error){self.postMessage({error:error.message})}};
