import React from "react";
import {
  Flex,
  Box,
  VStack,
  Button,
  Divider,
  Icon,
  Spacer,
} from "@chakra-ui/react";
import { SlChart, SlCalculator, SlClock, SlLogout } from "react-icons/sl";

interface HeaderProps {
  onLogout: () => void;
}

const Header: React.FC<HeaderProps> = ({ onLogout }) => {
  return (
    <Box height="100vh">
      <VStack
        spacing={3}
        divider={<Divider borderColor="white" />}
        align="stretch"
      >
        <Button
          as="a"
          href="/"
          colorScheme="white"
          variant="ghost"
          w="100px"
          h="100px"
          _hover={{ color: "lightblue" }}
        >
          <Flex direction="column" alignItems="center" justifyContent="center">
            <Icon as={SlChart} w={6} h={6} />
            Stocks
          </Flex>
        </Button>
        <Button
          as="a"
          href="/strategies"
          colorScheme="white"
          variant="ghost"
          w="100px"
          h="100px"
          _hover={{ color: "lightblue" }}
        >
          <Flex direction="column" alignItems="center" justifyContent="center">
            <Icon as={SlCalculator} w={6} h={6} />
            Strategies
          </Flex>
        </Button>
        <Button
          as="a"
          href="/trades"
          colorScheme="white"
          variant="ghost"
          w="100px"
          h="100px"
          _hover={{ color: "lightblue" }}
        >
          <Flex direction="column" alignItems="center" justifyContent="center">
            <Icon as={SlClock} w={6} h={6} />
            Trade History
          </Flex>
        </Button>
        <Spacer mb="450" />
        <Button
          as="a"
          href="/login"
          colorScheme="white"
          variant="ghost"
          w="100px"
          h="100px"
          _hover={{ color: "lightblue" }}
        >
          <Flex direction="column" alignItems="center" justifyContent="center">
            <Icon as={SlLogout} w={6} h={6} />
            Logout
          </Flex>
        </Button>
      </VStack>
    </Box>
  );
};

export default Header;
