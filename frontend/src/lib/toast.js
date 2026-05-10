import * as toast from '@zag-js/toast';

export const toaster = toast.createStore({
  placement: 'bottom-end',
  max: 8,
  gap: 12,
  offsets: '1rem',
});
