import React, { useState, useEffect } from "react"; // Import useState hook
import {
  Button,
  Flex,
  Center,
  Box,
  Heading,
  Table,
  Thead,
  Tbody,
  Tr,
  Td,
  Text,
  Grid,
} from "@chakra-ui/react";
import { WarningIcon } from "@chakra-ui/icons"; // Import warning icon

interface Stock {
  symbol: string;
  name: string;
  strategyId: number;
}

interface Strategy {
  id: number;
  name: string;
  stocks: Stock[];
}

interface StrategiesResponse {
  strategies: Strategy[];
}

const Strategies: React.FC = () => {
  const [strategies, setStrategies] = useState<Strategy[]>([]);

  useEffect(() => {
    void fetch("http://127.0.0.1:8000/strategies")
      .then(async (response) => await response.json())
      .then((data: StrategiesResponse) => {
        setStrategies(data.strategies);
      });
  }, []);

  function removeStock(
    strategy: Strategy,
    stock: Stock,
    strategies: Strategy[],
    setStrategies: React.Dispatch<React.SetStateAction<Strategy[]>>,
  ): void {
    fetch(
      `http://127.0.0.1:8000/strategies/${strategy.id}/stocks/${stock.symbol}`,
      {
        method: "DELETE",
      },
    )
      .then(() => {
        const updatedStrategies = strategies.map((s) => {
          if (s.id === strategy.id) {
            s.stocks = s.stocks.filter((s) => s.symbol !== stock.symbol);
          }
          return s;
        });
        setStrategies(updatedStrategies);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }

  return (
    <Box color="white">
      <Heading as="h1" size="xl" textAlign="center" mb="5">
        Strategies
      </Heading>
      <Grid templateColumns="repeat(3, 1fr)" gap={5}>
        {strategies.map((strategy) => (
          <Box key={strategy.id}>
            <Heading as="h2" size="md" textAlign="center">
              {strategy.name}
            </Heading>
            {strategy.stocks.length > 0 ? (
              <Table variant="simple">
                <Thead>
                  <Tr>
                    <Td>Symbol</Td>
                    <Td>Name</Td>
                    <Td></Td>{" "}
                    {/* Add an extra header cell for the remove button */}
                  </Tr>
                </Thead>
                <Tbody>
                  {strategy.stocks.map((stock: Stock, index: number) => (
                    <Tr key={stock.symbol}>
                      <Td>{stock.symbol}</Td>
                      <Td>{stock.name}</Td>
                      <Td>
                        <Button
                          size="sm"
                          onClick={() => {
                            removeStock(
                              strategy,
                              stock,
                              strategies,
                              setStrategies,
                            );
                          }}
                        >
                          X
                        </Button>
                      </Td>
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
                    No stocks have been selected to run this strategy
                  </Text>
                </Flex>
              </Center>
            )}
          </Box>
        ))}
      </Grid>
    </Box>
  );
};

export default Strategies;
