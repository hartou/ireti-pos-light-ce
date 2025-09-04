import React from 'react';
import {
  StripeTerminalProvider,
} from '@stripe/stripe-terminal-react-native';
import {
  fetchConnectionToken,
} from './apiClient';
import App from './App';

export default function Root() {
  return (
    <>
        <StripeTerminalProvider
          logLevel="verbose"
          tokenProvider={fetchConnectionToken}
        >
          <App/>
        </StripeTerminalProvider>
    </>
  );
}