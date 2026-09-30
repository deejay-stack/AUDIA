const key='audia-cart';
export function readCart() {
  try {const value=JSON.parse(sessionStorage.getItem(key)||'[]'); return Array.isArray(value)?value.filter(item=>Number.isInteger(item.id)&&Number.isInteger(item.qty)&&item.qty>0&&item.qty<=99).slice(0,50):[];}
  catch {return [];}
}
export function writeCart(items) {sessionStorage.setItem(key,JSON.stringify(items.map(({id,qty})=>({id,qty}))));}
