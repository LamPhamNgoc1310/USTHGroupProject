import * as React from 'react';
import {createRoot} from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx';

const root = createRoot(document.body);
root.render(
    <BrowserRouter>
        <App/>
    </BrowserRouter>
)
