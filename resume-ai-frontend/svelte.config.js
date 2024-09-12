import adapter from "@sveltejs/adapter-static";

const dev = process.env.NODE_ENV === "development";

export default {
  kit: {
    paths: {
      base: process.env.NODE_ENV === "production" ? "/resume-ai" : "",
    },
  },
};
