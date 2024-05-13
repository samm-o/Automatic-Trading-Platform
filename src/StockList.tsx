/* eslint-disable @typescript-eslint/naming-convention */
import React, { useEffect, useState } from "react";
import {
  Input,
  Select,
  Box,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
} from "@chakra-ui/react";
import { Link as RouterLink } from "react-router-dom";

type IndicatorValues = Record<
  string,
  {
    close?: number;
    rsi_14?: number;
    sma_20?: number;
    sma_50?: number;
  }
>;

function StockList(): JSX.Element {
  const [stocks, setStocks] = useState([]);
  const [indicator_values, setIndicatorValues] = useState<IndicatorValues>({});
  const [stock_filter, setFilter] = useState("");
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    const url =
      stock_filter !== ""
        ? `http://127.0.0.1:8000/?filter=${stock_filter}`
        : "http://127.0.0.1:8000";
    fetch(url)
      .then(async (response) => await response.json())
      .then((data) => {
        setStocks(data.stocks as never[]);
        setIndicatorValues(data.indicator_values as IndicatorValues);
      })
      .catch((error): void => {
        console.error("Error:", error);
      });
  }, [stock_filter]);

  const handleFilterChange = (
    event: React.ChangeEvent<HTMLSelectElement>,
  ): void => {
    setFilter(event.target.value);
  };

  const handleSearchChange = (
    event: React.ChangeEvent<HTMLInputElement>,
  ): void => {
    setSearchTerm(event.target.value);
  };

  const filteredStocks = stocks.filter((stock: { symbol: string }) =>
    stock.symbol.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  return (
    <>
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={4}
      >
        <Select
          placeholder="Select filter"
          onChange={handleFilterChange}
          color="#717171"
          width="30%"
        >
          <option value="new_closing_highs">New Closing Highs</option>
          <option value="new_closing_lows">New Closing Lows</option>
          <option value="rsi_overbought">RSI Overbought</option>
          <option value="rsi_oversold">RSI Oversold</option>
          <option value="above_sma_20">Above SMA 20</option>
          <option value="below_sma_20">Below SMA 20</option>
          <option value="above_sma_50">Above SMA 50</option>
          <option value="below_sma_50">Below SMA 50</option>
        </Select>
        <Input
          placeholder="Search for a specific stock"
          onChange={handleSearchChange}
          color="white"
          bg="#333"
          width="70%"
        />
      </Box>
      <Table variant="simple">
        <Thead>
          <Tr>
            <Th color="lightgray" fontSize="sm">
              Symbol
            </Th>
            <Th color="lightgray" fontSize="sm">
              Price
            </Th>
            <Th color="lightgray" fontSize="sm">
              RSI 14
            </Th>
            <Th color="lightgray" fontSize="sm">
              SMA 20
            </Th>
            <Th color="lightgray" fontSize="sm">
              SMA 50
            </Th>
          </Tr>
        </Thead>
      </Table>
      <Box>
        {" "}
        {/* Adjust the height as needed */}
        <Table variant="simple" size="sm" overflowY="scroll">
          <Tbody>
            {filteredStocks.map((stock: { symbol: string }, index) => (
              <Tr
                key={stock.symbol}
                bg={index % 2 === 0 ? "#717171" : "transparent"}
              >
                <Td color="white" fontSize="sm">
                  <RouterLink to={`/stock/${stock.symbol}`}>
                    {stock.symbol}
                  </RouterLink>
                </Td>
                <Td color="white" fontSize="sm">
                  {parseFloat(
                    (indicator_values[stock.symbol]?.close ?? 0).toString(),
                  ).toFixed(2)}
                </Td>
                <Td color="white" fontSize="sm">
                  {parseFloat(
                    (indicator_values[stock.symbol]?.rsi_14 ?? 0).toString(),
                  ).toFixed(2)}
                </Td>
                <Td color="white" fontSize="sm">
                  {parseFloat(
                    (indicator_values[stock.symbol]?.sma_20 ?? 0).toString(),
                  ).toFixed(2)}
                </Td>
                <Td color="white" fontSize="sm">
                  {parseFloat(
                    (indicator_values[stock.symbol]?.sma_50 ?? 0).toString(),
                  ).toFixed(2)}
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </Box>
    </>
  );
}

export default StockList;
