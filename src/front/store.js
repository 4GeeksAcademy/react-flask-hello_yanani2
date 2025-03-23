export const initialStore = () => {
  const token = localStorage.getItem("token");
  const userStr = localStorage.getItem("user");
  let user = null;

  if (userStr) {
    try {
      user = JSON.parse(userStr);
    } catch (e) {
      console.error("Error al parsear usuario", e);
    }
  }

  return {
    message: null,

    token: token || null,
    user: user || null,
    error: null,

    notes: [],
  };
};

export default function storeReducer(store, action = {}) {
  switch (action.type) {
    case "set_hello":
      return {
        ...store,
        message: action.payload,
      };

    case "login":
      localStorage.setItem("token", action.payload.token);
      localStorage.setItem("user", JSON.stringify(action.payload.user));

      return {
        ...store,
        token: action.payload.token,
        user: action.payload.user,
        error: null,
      };

    case "logout":
      localStorage.removeItem("token");
      localStorage.removeItem("user");

      return {
        ...store,
        token: null,
        user: null,
        notes: [],
      };

    case "set_error":
      return {
        ...store,
        error: action.payload,
      };

    case "load_notes":
      return {
        ...store,
        notes: action.payload,
      };

    default:
      return store;
  }
}
