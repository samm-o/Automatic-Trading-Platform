import React, { useEffect, useState } from "react";
import {
  Table,
  Th,
  Tr,
  Td,
  Thead,
  Tbody,
  Flex,
  Box,
  Text,
  Heading,
  Button,
  Select,
} from "@chakra-ui/react";
import { AdvancedChart } from "react-tradingview-embed";
import { useParams, Link } from "react-router-dom";
import { InfoIcon } from "@chakra-ui/icons";
import "./App.css";

interface ResponseData {
  bars: Bar[];
  stock_id: number;
}

interface Bar {
  datetime: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

function StockDetails(): JSX.Element {
  const { symbol } = useParams<{ symbol: string }>();
  const [bars, setBars] = useState<Bar[]>([]);
  const [selectedStrategy, setSelectedStrategy] = useState<string | null>(null);
  const [stockId, setStockId] = useState<number | null>(null);

  useEffect(() => {
    // Fetch the stock's data when the selected stock changes
    if (symbol !== null && symbol !== undefined && symbol !== "") {
      fetch(`http://127.0.0.1:8000/stock/${symbol}`)
        .then(
          async (response) => await (response.json() as Promise<ResponseData>),
        )
        .then((data) => {
          setBars(data.bars);
          setStockId(data.stock_id);
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    }
  }, [symbol]);

  const handleStrategyChange = (
    event: React.ChangeEvent<HTMLSelectElement>,
  ): void => {
    setSelectedStrategy(event.target.value);
  };

  const handleApplyStrategy = async (): Promise<void> => {
    if (selectedStrategy !== null && stockId !== null) {
      console.log(stockId);
      const strategyIdMap: Record<string, number> = {
        "Opening range breakout": 1,
        "Opening range breakdown": 2,
        "Bollinger bands": 3,
      };
      const strategyId = strategyIdMap[selectedStrategy];
      console.log(strategyId);
      const response = fetch("http://127.0.0.1:8000/apply_strategy", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          strategy_id: strategyId.toString(),
          stock_id: stockId.toString(),
        }),
      });
      if ((await response).ok) {
        // Redirect to the strategy page
        window.location.href = `/strategies`;
      } else {
        // Handle error
        console.error("Failed to apply strategy");
      }
    }
  };

  return (
    <>
      <Box>
        <div className="chart-container">
          <AdvancedChart
            widgetProps={{
              symbol,
              theme: "dark",
              autosize: true,
            }}
          />
        </div>
      </Box>
      <Box>
        {symbol !== null && symbol !== undefined ? (
          <>
            <Flex
              justifyContent="space-between"
              alignItems="center"
              maxHeight="5vh"
            >
              <Heading as="h2" size="md" color="white" mb={4}>
                {symbol}&rsquo;s Daily price action
              </Heading>
              <Flex>
                <Select
                  placeholder="Select strategy"
                  onChange={handleStrategyChange}
                  color="#717171"
                  width="170px"
                >
                  <option value="Opening range breakout">
                    Opening range breakout
                  </option>
                  <option value="Opening range breakdown">
                    Opening range breakdown
                  </option>
                  <option value="Bollinger bands">Bollinger bands</option>
                </Select>
                <Link to="/strategies">
                  <Button
                    colorScheme="blue"
                    onClick={() => {
                      void handleApplyStrategy();
                    }}
                    ml={4}
                  >
                    Apply Strategy
                  </Button>
                </Link>
              </Flex>
            </Flex>
            <Box overflowY="auto" maxHeight="25vh">
              <Table variant="striped" size="sm" colorScheme="white">
                <Thead>
                  <Tr>
                    <Th color="white">Date</Th>
                    <Th color="white">Open</Th>
                    <Th color="white">High</Th>
                    <Th color="white">Low</Th>
                    <Th color="white">Close</Th>
                    <Th color="white">Volume</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {bars.map((bar, index) => (
                    <Tr
                      key={bar.datetime}
                      bg={index % 2 === 0 ? "#717171" : "transparent"}
                    >
                      <Td color="white">{bar.datetime}</Td>
                      <Td color="white">{bar.open}</Td>
                      <Td color="white">{bar.high}</Td>
                      <Td color="white">{bar.low}</Td>
                      <Td color="white">{bar.close}</Td>
                      <Td color="white">{bar.volume}</Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            </Box>
          </>
        ) : (
          <Flex
            direction="column"
            alignItems="center"
            justifyContent="center"
            height="30vh"
          >
            <InfoIcon boxSize="50px" />
            <Text fontSize="xl" fontWeight="bold" color="white" mt={4}>
              No stock selected
            </Text>
          </Flex>
        )}
      </Box>
    </>
  );
}

export default StockDetails;
