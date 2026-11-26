import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { Demo } from './Demo';
import { messages } from './messages';
import './demo.css';

const root = document.getElementById('demo-root');
if (!root) throw new Error('Demo root is missing');

document.title = messages.pageTitle;
root.dataset.bundle = 'SEBAVERSE_LOCAL_TEACHING_DEMO_ONLY';
createRoot(root).render(
  <StrictMode>
    <Demo />
  </StrictMode>,
);
