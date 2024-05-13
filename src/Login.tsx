import React, { useState } from "react";
import { css, Global } from "@emotion/react";
import {
  Box,
  FormControl,
  FormLabel,
  Input,
  Button,
  useToast,
  Heading,
  VStack,
} from "@chakra-ui/react";

interface LoginResponse {
  success: boolean;
  // include other properties as needed
}

interface LoginProps {
  onLogin: () => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const toast = useToast();

  const handleSubmit = (event: React.FormEvent): void => {
    event.preventDefault();

    fetch("http://127.0.0.1:8000/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    })
      .then(
        async (response) => await (response.json() as Promise<LoginResponse>),
      )
      .then((data) => {
        if (data.success) {
          onLogin();
          window.location.href = "/";
        } else {
          toast({
            title: "Invalid credentials.",
            description: "Username or password is incorrect.",
            status: "error",
            duration: 9000,
            isClosable: true,
          });
        }
      })
      .catch((error) => {
        toast({
          title: "An error occurred.",
          description: `Unable to login at this time. Error: ${error.message}`,
          status: "error",
          duration: 9000,
          isClosable: true,
        });
      });
  };

  return (
    <>
      <Global
        styles={css`
          body {
            background-color: #333;
          }
        `}
      />
      <VStack alignItems="center" justifyContent="center" height="100vh">
        <Heading as="h1" size="xl" color="white" textAlign="center">
          Login
        </Heading>
        <Box
          bg="#232322"
          color="white"
          w="500px"
          h="300px"
          p="6"
          mt="8"
          borderRadius="lg"
        >
          <form onSubmit={handleSubmit}>
            <FormControl id="username" isRequired>
              <FormLabel>Username</FormLabel>
              <Input
                type="text"
                onChange={(e) => {
                  setUsername(e.target.value);
                }}
              />
            </FormControl>
            <FormControl id="password" isRequired mt={6}>
              <FormLabel>Password</FormLabel>
              <Input
                type="password"
                onChange={(e) => {
                  setPassword(e.target.value);
                }}
              />
            </FormControl>
            <Button mt={6} colorScheme="teal" type="submit">
              Login
            </Button>
          </form>
        </Box>
      </VStack>
    </>
  );
};

export default Login;
