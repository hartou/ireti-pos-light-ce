import React, {useEffect, useState} from 'react';
import {
  TouchableOpacity,
  Text,
  PermissionsAndroid,
  Platform,
  Alert,
  StyleSheet,
  ActivityIndicator,
  View,
} from 'react-native';
import {
  useStripeTerminal,
} from '@stripe/stripe-terminal-react-native';
import {
  fetchPaymentIntent,
  capturePaymentIntent,
} from './apiClient';

export default function App() {
  const {
    discoverReaders,
    connectReader,
    retrievePaymentIntent,
    collectPaymentMethod,
    confirmPaymentIntent,
    setSimulatedCard,
  } = useStripeTerminal({
    onUpdateDiscoveredReaders: async (readers) => {
      const selectedReader = readers[0];
      const { reader, error } = await connectReader(
        { reader: selectedReader, locationId: selectedReader.locationId },
        'bluetoothScan'
      );

      if (error) {
        console.log('connectReader error', error);
      } else {
        console.log('Reader connected successfully', reader);
      }
    },
  });
  const [permissionsGranted, setPermissionsGranted] = useState(false);

  useEffect(() => {
    async function init() {
      try {
        const granted = await PermissionsAndroid.request(
          'android.permission.ACCESS_FINE_LOCATION',
          {
            title: 'Location Permission',
            message: 'Stripe Terminal needs access to your location',
            buttonPositive: 'Accept',
          },
        );
        if (granted === PermissionsAndroid.RESULTS.GRANTED) {
          console.log('You can use the Location');
          setPermissionsGranted(true);
        } else {
          Alert.alert(
            'Location services are required to connect to a reader.',
          );
        }
      } catch {
        Alert.alert(
          'Location services are required to connect to a reader.',
        );
      }
    }

    if (Platform.OS === 'android') {
      init();
    } else {
      setPermissionsGranted(true);
    }
  }, []);

  const handleDiscoverReaders = async () => {
    // List of discovered readers will be available within useStripeTerminal hook
    const {error} = await discoverReaders({
      discoveryMethod: 'bluetoothScan',
      simulated: true,
    });

    if (error) {
      console.log(
        'Discover readers error: ',
        `${error.code}, ${error.message}`,
      );
    } else {
      console.log('discoverReaders succeeded');
    }
  };

  const collectPayment = async () => {
    const clientSecret = await fetchPaymentIntent();

    await setSimulatedCard("4242424242424242");

    if (!clientSecret) {
      console.log('createPaymentIntent failed');
      return;
    }
    const {paymentIntent, error} = await retrievePaymentIntent(clientSecret);

    if (error) {
      console.log(`Couldn't retrieve payment intent: ${error.message}`);
    } else if (paymentIntent) {
      const {paymentIntent: collectedPaymentIntent, error: collectError} =
        await collectPaymentMethod(paymentIntent.id);

      if (collectError) {
        console.log(`collectPaymentMethod failed: ${collectError.message}`);
      } else if (collectedPaymentIntent) {
        console.log('collectPaymentMethod succeeded');

        processPayment(collectedPaymentIntent);
      }
    }
  };

  const processPayment = async (paymentIntent) => {
    const {paymentIntent: processPaymentPaymentIntent, error} =
      await confirmPaymentIntent(paymentIntent);

    if (error) {
      console.log(`confirmPaymentIntent failed: ${error.message}`);
    } else if (processPaymentPaymentIntent) {
      console.log('confirmPaymentIntent succeeded');

      const result = await capturePaymentIntent();
      if (!result) {
        console.log('capture failed');
      } else {
        console.log('capture succeeded');
      }
    }
  };

  return (
    <>
      {permissionsGranted ? (
        <View style={styles.container}>
          <TouchableOpacity
            disabled={!permissionsGranted}
            onPress={handleDiscoverReaders}
          >
            <Text>Discover Readers</Text>
          </TouchableOpacity><TouchableOpacity
            disabled={!permissionsGranted}
            onPress={collectPayment}
          >
            <Text>Collect payment</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <ActivityIndicator style={StyleSheet.absoluteFillObject} />
      )}
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center', // Center vertically
    alignItems: 'center', // Center horizontally
  },
});