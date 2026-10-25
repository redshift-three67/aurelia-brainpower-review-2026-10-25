import { caseJobGuard } from './job-context.js';
export function personalRequest(binding,{database,mode,seed,weight,requestId}) {
 const guard=caseJobGuard(binding);
 if(!guard.expected_case_ref || !guard.expected_context_version) throw new Error('Persönlicher Fall muss zuerst gespeichert und geladen sein.');
 if(!['seeded','stochastic'].includes(mode)) throw new Error('Zufallsmodus muss bewusst ausgewählt werden.');
 return {...guard,request_id:requestId,database,mode,seed:mode==='stochastic'?null:(seed ?? 0),weight};
}
export function personalPage(job,page) {
 return job?.status==='completed' ? job.rows.slice((page-1)*21,page*21) : [];
}
