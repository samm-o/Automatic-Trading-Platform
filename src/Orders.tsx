import React, { useEffect, useState } from "react";
import {
  Center,
  Flex,
  Box,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Text,
  Heading,
} from "@chakra-ui/react";
import { WarningIcon } from "@chakra-ui/icons";

interface Trade {
  contract: {
    lastTradeDateOrContractMonth: string;
    symbol: string;
  };
  order: {
    action: string;
    filledQuantity: number;
  };
  fills: [
    {
      commissionReport: {
        realizedPNL: number;
      };
    },
  ];
}

const Orders: React.FC = () => {
  const [trades, setTrades] = useState<Trade[]>([]);

  useEffect(() => {
    const fetchTrades = async (): Promise<void> => {
      try {
        const response = await fetch("/trades");
        const data: { trades: Trade[] } = await response.json();
        setTrades(data.trades);
      } catch (error) {
        console.error("Error fetching trades:", error);
      }
    };

    void fetchTrades();
  }, []);

  return (
    <Box
      color="white"
      h="100vh"
      display="flex"
      flexDirection="column"
      justifyContent="flex-start"
      alignItems="center"
    >
      <Heading as="h1" size="xl" textAlign="center" mb="5">
        Orders
      </Heading>
      {trades.length > 0 ? (
        <Table variant="simple">
          <Thead>
            <Tr>
              <Th>Date</Th>
              <Th>Symbol</Th>
              <Th>Action</Th>
              <Th>Filled Quantity</Th>
              <Th>Realized PNL</Th>
            </Tr>
          </Thead>
          <Tbody>
            {trades.map((trade) => (
              <Tr key={trade.contract.symbol}>
                <Td>{trade.contract.lastTradeDateOrContractMonth}</Td>
                <Td>{trade.contract.symbol}</Td>
                <Td>{trade.order.action}</Td>
                <Td>{trade.order.filledQuantity}</Td>
                <Td>{trade.fills[0].commissionReport.realizedPNL}</Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      ) : (
        <Center height="50vh">
          <Flex
            flexDirection="column"
            alignItems="center"
            justifyContent="center"
          >
            <WarningIcon boxSize={70} />
            <Text fontSize="lg" textAlign="center">
              No trades have been made today
            </Text>
          </Flex>
        </Center>
      )}
    </Box>
  );
};

export default Orders;
