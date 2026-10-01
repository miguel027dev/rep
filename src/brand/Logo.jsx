import React from 'react';
export function BrandMark(){return <svg viewBox="0 0 64 64" aria-hidden="true"><path fill="currentColor" d="M12 8h20c11 0 18 7 18 17 0 7-4 13-10 16l12 15H39L23 35h9c6 0 9-4 9-10s-3-9-9-9H22v40H12V8Z"/></svg>}
export default function Logo({small=false}){return <div className={'logo rep-wordmark '+(small?'small':'')} aria-label="REP"><BrandMark/>{!small&&<span>REP</span>}</div>}
