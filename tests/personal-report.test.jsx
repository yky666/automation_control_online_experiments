import React from 'react';
import {describe,it,expect,vi,beforeEach} from 'vitest';
import {render,screen,fireEvent,cleanup} from '@testing-library/react';
import {PersonalReport} from '../frontend/PersonalReport.jsx';
import {emptyReport,snapshotRun,reportSections,captureRun,readReport,wordReport,pdfReport} from '../frontend/personal-report.js';
import fs from 'node:fs';
beforeEach(()=>{cleanup();localStorage.clear()});
const run={time:[0,.5,1],input:[1,1,1],output:[0,.4,.63],traces:{scope:[0,.4,.63]},engine:'browser-signal',method:'隐式欧拉',createdAt:'2026-10-22',graph:{nodes:[],edges:[]},request:{lab_id:3,task_id:'test'}};
describe('personal report',()=>{
 it('edits identity and content, preserves drafts and selects actual runs',()=>{captureRun(run,'自建模型');render(<PersonalReport open onClose={()=>{}}/>);fireEvent.change(screen.getByLabelText('姓名'),{target:{value:'张三'}});fireEvent.change(screen.getByLabelText('学号'),{target:{value:'2026001'}});fireEvent.change(screen.getByLabelText('实验内容（可填写自主扩展实验）'),{target:{value:'比较两种增益'}});expect(readReport().name).toBe('张三');expect(readReport().content).toBe('比较两种增益');fireEvent.click(screen.getByRole('checkbox'));expect(reportSections(readReport()).some(s=>s.run)).toBe(false);});
 it('captures immutable bounded snapshots including last point',()=>{const r={...run,time:Array.from({length:20001},(_,i)=>i/1000),input:Array(20001).fill(1),output:Array(20001).fill(2),traces:{}};const s=snapshotRun(r,'测试');expect(s.time).toHaveLength(1001);expect(s.time.at(-1)).toBe(20);r.output[0]=99;expect(s.series.output[0]).toBe(2);expect(()=>snapshotRun({...run,output:[NaN]},'bad')).toThrow();});
 it('creates genuine docx and paginated Chinese PDF with selected run charts',async()=>{const d={...emptyReport(),name:'张三',studentId:'2026001',content:'个性化实验内容\n'.repeat(100),runs:[snapshotRun(run,'自主扩展实验')]};const png=Uint8Array.from(Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aHoQAAAAASUVORK5CYII=','base64'));const doc=await wordReport(d,()=>png);expect(doc.size).toBeGreaterThan(1000);const pdf=await pdfReport(d,fs.readFileSync('assets/fonts/NotoSansSC-Regular.ttf'));expect(Buffer.from(pdf).subarray(0,5).toString()).toBe('%PDF-');const {PDFDocument}=await import('pdf-lib');expect((await PDFDocument.load(pdf)).getPageCount()).toBeGreaterThan(2);fs.writeFileSync('/tmp/control-report-qa.pdf',pdf);},60000);
});
