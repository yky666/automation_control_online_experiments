import {vi} from 'vitest';
globalThis.ResizeObserver=class {observe(){} disconnect(){}};
HTMLElement.prototype.scrollTo=vi.fn();
URL.createObjectURL=vi.fn(()=>'blob:report');URL.revokeObjectURL=vi.fn();
