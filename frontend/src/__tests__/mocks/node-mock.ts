// src/mocks/node.js
import { setupServer } from 'msw/node';
import { handlers } from './handler-mock';

export const server = setupServer(...handlers);
