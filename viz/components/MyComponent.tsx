import { Application } from '@pixi/react';
import { useRef } from 'react';

const MyComponent = () => {
    const parentRef = useRef(null);

    return (
        <div ref={parentRef}>
            <Application resizeTo={parentRef} />
        </div>
    );
};
