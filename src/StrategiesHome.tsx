import React from "react";
import { Flex, Box, HStack } from "@chakra-ui/react";
import Header from "./Header";
import Strategies from "./Strategies";

interface HomeProps {
  onLogout: () => void;
}

const StrategiesHome: React.FC<HomeProps> = ({ onLogout }) => {
  return (
    <HStack spacing={0} h="100vh">
      <Box bg="#333" w="100px" h="100%" color="white">
        <Header onLogout={onLogout} />
      </Box>
      <Flex direction="row" bg="#111" h="100%" w="100%" flex="1">
        <Box bg="#111" h="100%" w="100%" overflowY="auto">
          <Strategies />
        </Box>
      </Flex>
    </HStack>
  );
};

export default StrategiesHome;
