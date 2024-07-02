# real-time-communication-practice
클라이언트와 서버가 실시간 통신을 통해 알림 등을 받도록 실습하는 repo


## goal

아래의 기능들을 예습하고 차이점을 정리해보기

1. polling
2. long polling
3. web socket
4. sse 

## polling

### 특징
1. 주기적인 클라이언트-서버 통신
    - 클라이언트가 주기적으로 서버에 데이터 변화 여부를 확인하기 위해 요청을 보냄
    - 서버는 응답에 변경된 데이터를 포함하여 전달
2. 데이터 변경 감지 방식
    - 클라이언트가 직접 서버에 변경 사항을 확인하는 능동적인 통신 방식
3. 높은 네트워크 오버헤드
    - 불필요한 요청/응답 교환으로 인해 네트워크 부하가 큼
4. 실시간성 제한
    - 폴링 주기에 따라 데이터 전송 지연이 발생할 수 있어 실시간성이 떨어짐

### 동작 방식

Polling은 클라이언트가 주기적으로 서버에 데이터 변경 여부를 확인하는 방식입니다. 동작 방식은 다음과 같습니다:

1. **클라이언트 요청**
   - 클라이언트가 주기적으로 서버에 데이터 변경 여부를 확인하는 요청을 보냅니다.

2. **서버 응답**
   - 서버는 클라이언트의 요청을 받고, 현재 데이터 상태를 확인합니다.
   - 데이터가 변경되었다면 변경된 데이터를 클라이언트에게 전송합니다.
   - 데이터가 변경되지 않았다면 "데이터 없음" 등의 응답을 클라이언트에게 보냅니다.

3. **클라이언트 처리**
   - 클라이언트는 서버의 응답을 받아 데이터를 갱신하거나 다음 요청을 준비합니다.

4. **주기적 반복**
   - 클라이언트는 일정 시간이 지나면 다시 서버에 데이터 변경 여부를 확인하는 요청을 보냅니다.

### 코드
- client 측에서 일정 주기마다 API 호출을 하면 된다.

- server
```python
@router.get("/polling", description="polling을 구현한 api")
async def polling():
    message = await message_view("Polling")
    return {"message": message}
```

- client
```javascript
function fetchPolling() {
        fetch('/polling')
            .then(response => response.json())
            .then(data => {
                console.log("message", data);
                updateComponent("polling-container", data.message);
            })
            .catch(error => {
                console.error('Error fetching component:', error);
            });
    }

// 주기적으로 데이터 변화 확인
 setInterval(fetchPolling, pollingInterval);
```

## Long-polling 

### 특징

1. **실시간 데이터 전송**: Long Polling은 클라이언트와 서버 간의 지속적인 연결을 통해 실시간으로 데이터를 전송할 수 있습니다. 클라이언트가 요청을 보내면 서버는 새로운 데이터가 생길 때까지 응답을 지연시키다가, 데이터가 생기면 즉시 클라이언트에게 전송합니다.
2. **HTTP 기반**: Long Polling은 HTTP 프로토콜을 사용하므로 기존 웹 애플리케이션 인프라를 활용할 수 있습니다. 웹소켓과 달리 별도의 프로토콜을 지원할 필요가 없습니다.
3. **단순한 구현**: Long Polling은 클라이언트가 지속적으로 서버에 요청을 보내는 방식이므로, 구현이 WebSocket에 비해 상대적으로 간단합니다.
4. **연결 유지 필요**: Long Polling은 클라이언트와 서버 간의 연결을 유지해야 하므로, 장기 연결로 인한 리소스 소모가 있을 수 있습니다.
5. **지연 시간 발생**: 서버가 새로운 데이터를 기다리는 동안 클라이언트는 대기해야 하므로, 지연 시간이 발생할 수 있습니다.
6. **브라우저 호환성**: HTTP 기반이므로 대부분의 브라우저에서 동작하지만, 일부 오래된 브라우저에서는 지원되지 않을 수 있습니다.

### 동작 방식

1. 클라이언트가 서버에 데이터 요청 메시지를 보냅니다.
2. 서버는 클라이언트의 요청을 받고, 데이터를 즉시 보낼 수 없는 경우 응답을 지연시킵니다.
3. 서버에 새로운 데이터가 생기면 클라이언트에게 응답을 보냅니다.
4. 클라이언트는 응답을 받으면 다시 새로운 요청을 보냅니다.
5. 이 과정을 반복하며 실시간 데이터 업데이트를 구현합니다.

### 코드
- fastapi의 비동기 router를 처리하는 방법 때문에 while이 돌고 있을 때 아래의 비동기 로직을 넣어주어서 이벤트 루프가 블로킹 되는 부분을 없애줘야함
- 만약 이렇게 안하고 싶으면 router handler를 동기로 작동하도록 해서 다른 스레드에서 돌도록 해야함
```python
# server
@router.get("/long-polling", description="long-polling을 구현한 api")
async def long_polling():
    global event_msg
    while True:
         if event_msg != "Not Event":
            event_msg = "Not Event"
            message = await message_view("Long Polling")
            response_data = {"message": message}
            return response_data
        await asyncio.sleep(0) # 동기 코드인 while 문이 event loop를 블로킹 시키기 때문에 논블로킹을 위한 비동기 코드 삽입
```

- client
```javascript
function fetchLongPolling() {
        fetch('/long-polling')
            .then(response => response.json())
            .then(data => {
                updateComponent("long-polling-container", data.message);
                setTimeout(fetchLongPolling, 0);  // 즉시 다음 요청 보내기
            })
            .catch(error => {
                console.error('Error fetching data:', error);
                setTimeout(fetchLongPolling, 5000);  // 5초 후 재시도
            });
    }

    fetchLongPolling();
```


## SSE

알겠습니다. Server-Sent Events(SSE)의 주요 특징과 동작 방식을 정리해 드리겠습니다.

### 특징

1. **서버 주도 이벤트 전송**: SSE는 서버가 클라이언트에게 이벤트를 전송하는 방식입니다. 클라이언트는 서버에 연결만 해두면 서버가 이벤트를 보냅니다.

2. **HTTP 기반**: SSE는 HTTP 프로토콜을 사용하므로 기존 웹 인프라를 활용할 수 있습니다.

3. **단방향 통신**: SSE는 서버에서 클라이언트로 한 방향으로만 데이터가 전송됩니다. 클라이언트는 이벤트를 받기만 할 뿐 서버에 요청을 보내지 않습니다.

4. **연결 유지**: SSE는 연결을 유지하며 지속적으로 이벤트를 전송할 수 있습니다. 연결이 끊기면 클라이언트는 다시 연결해야 합니다.

5. **브라우저 호환성**: 대부분의 최신 브라우저에서 SSE를 지원하지만, 일부 오래된 브라우저에서는 지원되지 않을 수 있습니다.

## 동작 방식

1. **클라이언트 연결**
   - 클라이언트가 서버의 SSE 엔드포인트에 연결합니다.

2. **서버 이벤트 전송**
   - 서버는 클라이언트에게 데이터 변경 이벤트가 발생할 때마다 이를 전송합니다.
   - 이벤트 데이터는 텍스트 형식으로 전송됩니다.

3. **클라이언트 처리**
   - 클라이언트는 서버에서 전송된 이벤트 데이터를 받아 처리합니다.
   - 클라이언트는 이벤트 데이터를 실시간으로 갱신할 수 있습니다.

4. **연결 유지**
   - 클라이언트와 서버 간의 연결은 유지되며, 서버는 새로운 이벤트가 발생할 때마다 지속적으로 데이터를 전송합니다.
   - 연결이 끊기면 클라이언트는 다시 연결해야 합니다.

SSE는 Polling이나 Long Polling과 달리 서버 주도의 실시간 통신 방식을 제공합니다. 구현이 상대적으로 간단하고 HTTP 프로토콜을 활용할 수 있다는 장점이 있습니다.

### 코드

- server
```python

@router.get("/sse", description="SSE를 구현한 api")
async def sse_endpoint():
    async def event_generator():
        while True:
            message = await message_view("SSE")
            message = {"message": message}
            yield f"data: {json.dumps(message)}\n\n"
            await asyncio.sleep(1)  # 1초마다 이벤트 전송

    return StreamingResponse(event_generator(), media_type="text/event-stream")

```

- client 
```javascript
const eventSource = new EventSource('/sse');

    eventSource.addEventListener('message', (event) => {
      const data = JSON.parse(event.data);
      console.log("SSE", data);
      updateComponent("sse-container", data.message)
    });

    eventSource.addEventListener('error', (event) => {
      console.error('EventSource error:', event);
    });
```