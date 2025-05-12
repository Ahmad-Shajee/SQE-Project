import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Register from "../components/register"; // adjust path if needed
import { BrowserRouter } from "react-router-dom";

// Mock useNavigate and clear mocks in beforeEach
const mockNavigate = jest.fn();

jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockNavigate,
}));

beforeEach(() => {
  jest.clearAllMocks();
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve({ userId: "12345" }),
    })
  );
  Storage.prototype.setItem = jest.fn();
});

test("renders registration form with all input fields", () => {
  render(
    <BrowserRouter>
      <Register />
    </BrowserRouter>
  );

  expect(screen.getByPlaceholderText("Enter your username")).toBeInTheDocument();
  expect(screen.getByPlaceholderText("Enter your email")).toBeInTheDocument();
  expect(screen.getByPlaceholderText("Enter your password")).toBeInTheDocument();
  expect(screen.getByPlaceholderText("Confirm your password")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /register/i })).toBeInTheDocument();
});

test("shows error message when passwords do not match", async () => {
    render(
      <BrowserRouter>
        <Register />
      </BrowserRouter>
    );
  
    fireEvent.change(screen.getByPlaceholderText("Enter your username"), {
      target: { value: "testuser" },
    });
  
    fireEvent.change(screen.getByPlaceholderText("Enter your email"), {
      target: { value: "test@example.com" },
    });
  
    fireEvent.change(screen.getByPlaceholderText("Enter your password"), {
      target: { value: "password123" },
    });
  
    fireEvent.change(screen.getByPlaceholderText("Confirm your password"), {
      target: { value: "password321" },
    });
  
    fireEvent.click(screen.getByRole("button", { name: "Register" }));
  
    expect(await screen.findByText("Passwords do not match")).toBeInTheDocument();
  });
  
test("shows backend error message on failed registration", async () => {
    // Mock failed fetch response
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: false,
        json: () => Promise.resolve({ message: "Email already exists" }),
      })
    );
  
    render(
      <BrowserRouter>
        <Register />
      </BrowserRouter>
    );
  
    fireEvent.change(screen.getByPlaceholderText("Enter your username"), {
      target: { value: "testuser" },
    });
  
    fireEvent.change(screen.getByPlaceholderText("Enter your email"), {
      target: { value: "existing@example.com" },
    });
  
    fireEvent.change(screen.getByPlaceholderText("Enter your password"), {
      target: { value: "password123" },
    });
  
    fireEvent.change(screen.getByPlaceholderText("Confirm your password"), {
      target: { value: "password123" },
    });
  
    fireEvent.click(screen.getByRole("button", { name: "Register" }));
  
    // Wait for error message to appear
    await waitFor(() =>
      expect(screen.getByText("Email already exists")).toBeInTheDocument()
    );
  });


  test("submits form successfully and navigates to dashboard", async () => {
    render(
      <BrowserRouter>
        <Register />
      </BrowserRouter>
    );
  
    fireEvent.change(screen.getByPlaceholderText("Enter your username"), {
      target: { value: "testuser" },
    });
  
    fireEvent.change(screen.getByPlaceholderText("Enter your email"), {
      target: { value: "test@example.com" },
    });
  
    fireEvent.change(screen.getByPlaceholderText("Enter your password"), {
      target: { value: "password123" },
    });
  
    fireEvent.change(screen.getByPlaceholderText("Confirm your password"), {
      target: { value: "password123" },
    });
  
    fireEvent.click(screen.getByRole("button", { name: "Register" }));
  
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(1);
      expect(fetch).toHaveBeenCalledWith(
        "http://localhost:5002/register",
        expect.objectContaining({
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            username: "testuser",
            email: "test@example.com",
            password: "password123",
          }),
        })
      );
      expect(localStorage.setItem).toHaveBeenCalledWith("username", "testuser");
      expect(localStorage.setItem).toHaveBeenCalledWith("userId", "12345");
      expect(mockNavigate).toHaveBeenCalledWith("/dashboard");
    });
  });

  test("handles network or unexpected error gracefully", async () => {
    // Mock a failed fetch request (e.g., network issue)
    global.fetch = jest.fn(() => Promise.reject("Network Error"));
  
    render(
      <BrowserRouter>
        <Register />
      </BrowserRouter>
    );
  
    fireEvent.change(screen.getByPlaceholderText("Enter your username"), {
      target: { value: "testuser" },
    });
  
    fireEvent.change(screen.getByPlaceholderText("Enter your email"), {
      target: { value: "test@example.com" },
    });
  
    fireEvent.change(screen.getByPlaceholderText("Enter your password"), {
      target: { value: "password123" },
    });
  
    fireEvent.change(screen.getByPlaceholderText("Confirm your password"), {
      target: { value: "password123" },
    });
  
    fireEvent.click(screen.getByRole("button", { name: "Register" }));
  
    // Wait for the error message to appear
    await waitFor(() =>
      expect(screen.getByText("An error occurred. Please try again later.")).toBeInTheDocument()
    );
  });