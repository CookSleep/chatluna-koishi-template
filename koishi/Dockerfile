FROM koishijs/koishi:latest

WORKDIR /koishi

ARG NPM_REGISTRY=https://registry.npmjs.org

COPY package.json .yarnrc.yml ./
RUN corepack enable \
  && yarn config set npmRegistryServer "$NPM_REGISTRY" \
  && yarn install

COPY koishi.yml ./

CMD ["yarn", "start"]
