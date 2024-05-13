import React from "react";
import { Flex, Box, HStack } from "@chakra-ui/react";
import Header from "./Header";
import Orders from "./Orders";

interface HomeProps {
  onLogout: () => void;
}

const OrdersHome: React.FC<HomeProps> = ({ onLogout }) => {
  return (
    <HStack spacing={0} h="100vh">
      <Box bg="#333" w="100px" h="100%" color="white">
        <Header onLogout={onLogout} />
      </Box>
      <Flex direction="row" bg="#111" h="100%" w="100%" flex="1">
        <Box bg="#111" h="100%" w="100%" overflowY="auto">
          <Orders />
        </Box>
      </Flex>
    </HStack>
  );
};

export default OrdersHome;
