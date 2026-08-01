import apiClient from "@/lib/api-client";

const ENDPOINT = "/faq/";

export async function fetchFaqs() {
  const { data } = await apiClient.get(ENDPOINT);
  return data;
}

export async function createFaq(payload) {
  const { data } = await apiClient.post(ENDPOINT, payload);
  return data;
}

export async function deleteFaq(id) {
  await apiClient.delete(`/faq/${id}`);
}