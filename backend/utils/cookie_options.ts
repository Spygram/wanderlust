// import { ACCESS_COOKIE_MAXAGE, NODE_ENV } from '../config/utils.js';
// const defaultMaxAge = 3600000;
// interface CookieObject {
//   httpOnly: boolean;
//   sameSite: 'lax' | 'strict' | 'none';
//   secure: boolean;
//   maxAge: number;
// }
// const maxAge =
//   typeof ACCESS_COOKIE_MAXAGE === 'string' ? parseInt(ACCESS_COOKIE_MAXAGE, 10) : defaultMaxAge;

// const validMaxAge = isNaN(maxAge) ? defaultMaxAge : maxAge;
// export const cookieOptions: CookieObject = {
//   httpOnly: true,
//   sameSite: NODE_ENV === 'development' ? 'lax' : 'none',
//   secure: NODE_ENV === 'development' ? false : true,
//   maxAge: validMaxAge,
// };

// import { ACCESS_COOKIE_MAXAGE, NODE_ENV } from '../config/utils.js';

// const defaultMaxAge = 3600000;
// const maxAge =
//   typeof ACCESS_COOKIE_MAXAGE === 'string' ? parseInt(ACCESS_COOKIE_MAXAGE, 10) : defaultMaxAge;
// const validMaxAge = isNaN(maxAge) ? defaultMaxAge : maxAge;

// const isHttps = process.env.USE_HTTPS === 'true';

// export const cookieOptions = {
//   httpOnly: true,
//   sameSite: 'lax',
//   secure: isHttps,
//   maxAge: validMaxAge,
// };

import { ACCESS_COOKIE_MAXAGE, NODE_ENV } from '../config/utils.js';

const defaultMaxAge = 3600000;
const maxAge =
  typeof ACCESS_COOKIE_MAXAGE === 'string' ? parseInt(ACCESS_COOKIE_MAXAGE, 10) : defaultMaxAge;
const validMaxAge = isNaN(maxAge) ? defaultMaxAge : maxAge;

const isHttps = process.env.USE_HTTPS === 'true';

interface CookieObject {
  httpOnly: boolean;
  sameSite: 'lax' | 'strict' | 'none';
  secure: boolean;
  maxAge: number;
}

export const cookieOptions: CookieObject = {
  httpOnly: true,
  sameSite: 'lax',
  secure: isHttps,
  maxAge: validMaxAge,
};
