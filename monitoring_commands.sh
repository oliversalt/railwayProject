#!/bin/bash

echo "🎛️  GOOGLE CLOUD RUN MONITORING COMMANDS"
echo "======================================="
echo ""
echo "📊 Check if your service is HOT or COLD:"
echo ""

echo "1️⃣  Quick Status Check:"
echo "   curl -s https://word-vector-api-822750671162.us-central1.run.app/loading-status | python3 -m json.tool"
echo ""

echo "2️⃣  Health Check:"
echo "   curl -s https://word-vector-api-822750671162.us-central1.run.app/health | python3 -m json.tool"
echo ""

echo "3️⃣  View Real-time Logs:"
echo "   gcloud run services logs read word-vector-api --region=us-central1 --limit=20"
echo ""

echo "4️⃣  Follow Live Logs (watch startup):"
echo "   gcloud run services logs tail word-vector-api --region=us-central1"
echo ""

echo "5️⃣  Check Service Status:"
echo "   gcloud run services describe word-vector-api --region=us-central1"
echo ""

echo "6️⃣  List All Revisions:"
echo "   gcloud run revisions list --service=word-vector-api --region=us-central1"
echo ""

echo "🔥 HOT vs COLD Detection:"
echo ""
echo "  🔥 HOT (Ready):   model_loaded: true, loading_progress: 100"
echo "  🧊 COLD (Loading): model_loaded: false, loading_progress: 0-99"
echo "  💤 SLEEPING:      No response or timeout"
echo ""

echo "⏱️  Timing Guide:"
echo ""
echo "  • First deployment: 5-10 minutes (downloads 128MB model)"
echo "  • Cold start (after sleep): 30-60 seconds (model cached)"  
echo "  • Hot response: <100ms"
echo "  • Sleep timeout: ~15 minutes of inactivity"
echo ""

echo "🎯 Performance Commands:"
echo ""
echo "  Test response time:"
echo "  time curl -s 'https://word-vector-api-822750671162.us-central1.run.app/similarity?word1=king&word2=queen'"
echo ""

echo "  Wake up service (if sleeping):"
echo "  curl https://word-vector-api-822750671162.us-central1.run.app/health"
echo ""

echo "💡 Pro Tips:"
echo ""
echo "  • The new progress bar shows loading status in real-time"
echo "  • Model only downloads once per deployment"
echo "  • Subsequent cold starts are much faster (cached model)"
echo "  • Monitor logs during startup to see progress"
echo ""

echo "🚀 Your Word Vector API is now ready with:"
echo "  ✅ Real-time loading progress bar"
echo "  ✅ Better error handling and logging"
echo "  ✅ Status monitoring endpoints"
echo "  ✅ Optimized startup process"
