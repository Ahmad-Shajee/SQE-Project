import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Login from "../components/login";
import { BrowserRouter } from "react-router-dom";

// Mock useNavigate to avoid actual routing
const mockNavigate = jest.fn();
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockNavigate,
}));

// Reset mocks before each test
beforeEach(() => {
  jest.clearAllMocks(); // Clear mocks before each test
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      json: () =>
        Promise.resolve({
          access_token: "token123",
          username: "testuser",
          userId: "12345",
        }),
    })
  );

  // Mock localStorage.setItem
  Storage.prototype.setItem = jest.fn();
});

// Test for successful login
test("submits form successfully and navigates to dashboard", async () => {
  render(
    <BrowserRouter>
      <Login />
    </BrowserRouter>
  );

  fireEvent.change(screen.getByPlaceholderText("Enter your email"), {
    target: { value: "test@example.com" },
  });

  fireEvent.change(screen.getByPlaceholderText("Enter your password"), {
    target: { value: "password123" },
  });

  fireEvent.click(screen.getByRole("button", { name: /login/i }));

  await waitFor(() => {
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:5001/login",
      expect.objectContaining({
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: "test@example.com",
          password: "password123",
        }),
      })
    );

    expect(localStorage.setItem).toHaveBeenCalledWith("username", "testuser");
    expect(localStorage.setItem).toHaveBeenCalledWith("token", "token123");
    expect(localStorage.setItem).toHaveBeenCalledWith("userId", "12345");

    expect(mockNavigate).toHaveBeenCalledWith("/dashboard");
  });
});

// Test for invalid credentials
test("shows error message for invalid credentials", async () => {
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: false,
      json: () => Promise.resolve({ message: "Invalid credentials. Please try again." }),
    })
  );

  render(
    <BrowserRouter>
      <Login />
    </BrowserRouter>
  );

  fireEvent.change(screen.getByPlaceholderText("Enter your email"), {
    target: { value: "wrong@example.com" },
  });

  fireEvent.change(screen.getByPlaceholderText("Enter your password"), {
    target: { value: "wrongpassword" },
  });

  fireEvent.click(screen.getByRole("button", { name: /login/i }));

  await waitFor(() => {
    expect(screen.getByText("Invalid credentials. Please try again.")).toBeInTheDocument();
  });
});

// Test for network or unexpected error
test("handles network or unexpected error gracefully", async () => {
    global.fetch = jest.fn(() => Promise.reject("Network Error")); // Simulate a network error
  
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
  
    fireEvent.change(screen.getByPlaceholderText("Enter your email"), {
      target: { value: "test@example.com" },
    });
  
    fireEvent.change(screen.getByPlaceholderText("Enter your password"), {
      target: { value: "password123" },
    });
  
    fireEvent.click(screen.getByRole("button", { name: /login/i }));
  
    await waitFor(() => {
      expect(screen.getByText("An error occurred. Please try again later.")).toBeInTheDocument();
    });
  });